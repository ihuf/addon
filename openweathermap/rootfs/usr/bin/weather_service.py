#!/usr/bin/env python3
"""
OpenWeatherMap Home Assistant Add-on
Fetches weather data and publishes to MQTT with Home Assistant Discovery
"""

import json
import logging
import os
import signal
import sys
import time
from typing import Any, Dict, Optional

import paho.mqtt.client as mqtt
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# OpenWeatherMap API endpoint
OWM_API_URL = "https://api.openweathermap.org/data/2.5/weather"

# MQTT Discovery prefix
DISCOVERY_PREFIX = "homeassistant"

# Device info for MQTT Discovery
DEVICE_INFO = {
    "identifiers": ["openweathermap_addon"],
    "name": "OpenWeatherMap",
    "manufacturer": "OpenWeatherMap",
    "model": "Weather API",
    "sw_version": "1.0.0"
}

# Sensor definitions: (name, unit, device_class, state_class, icon)
SENSORS = {
    "temperature": ("Temperature", None, "temperature", "measurement", "mdi:thermometer"),
    "feels_like": ("Feels Like", None, "temperature", "measurement", "mdi:thermometer"),
    "humidity": ("Humidity", "%", "humidity", "measurement", "mdi:water-percent"),
    "pressure": ("Pressure", "hPa", "pressure", "measurement", "mdi:gauge"),
    "wind_speed": ("Wind Speed", None, "wind_speed", "measurement", "mdi:weather-windy"),
    "wind_direction": ("Wind Direction", "°", None, "measurement", "mdi:compass"),
    "clouds": ("Cloud Coverage", "%", None, "measurement", "mdi:cloud"),
    "visibility": ("Visibility", "m", None, "measurement", "mdi:eye"),
    "weather_condition": ("Condition", None, None, None, "mdi:weather-partly-cloudy"),
    "weather_description": ("Description", None, None, None, "mdi:text"),
    "sunrise": ("Sunrise", None, "timestamp", None, "mdi:weather-sunset-up"),
    "sunset": ("Sunset", None, "timestamp", None, "mdi:weather-sunset-down"),
}


class WeatherService:
    """Main weather service class"""

    def __init__(self):
        self.running = True
        self.mqtt_client: Optional[mqtt.Client] = None
        self.config: Dict[str, Any] = {}
        self.mqtt_connected = False

        # Set up signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def load_config(self) -> bool:
        """Load configuration from options.json"""
        options_path = "/data/options.json"
        
        try:
            with open(options_path, "r") as f:
                self.config = json.load(f)
            
            # Validate required fields
            if not self.config.get("api_key"):
                logger.error("API key is required but not provided")
                return False
            
            # Set defaults
            self.config.setdefault("units", "metric")
            self.config.setdefault("language", "en")
            self.config.setdefault("update_interval", 600)
            self.config.setdefault("mqtt_host", "core-mosquitto")
            self.config.setdefault("mqtt_port", 1883)
            
            logger.info("Configuration loaded successfully")
            return True
            
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {options_path}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration: {e}")
            return False

    def get_unit_symbol(self, sensor_type: str) -> str:
        """Get the unit symbol based on units setting"""
        units = self.config.get("units", "metric")
        
        if sensor_type == "temperature":
            return "°C" if units == "metric" else "°F" if units == "imperial" else "K"
        elif sensor_type == "wind_speed":
            return "m/s" if units == "metric" else "mph" if units == "imperial" else "m/s"
        
        return ""

    def connect_mqtt(self) -> bool:
        """Connect to MQTT broker"""
        try:
            self.mqtt_client = mqtt.Client(client_id="openweathermap_addon")
            
            # Set credentials if provided
            username = self.config.get("mqtt_username")
            password = self.config.get("mqtt_password")
            if username:
                self.mqtt_client.username_pw_set(username, password)
            
            # Set callbacks
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            
            # Connect
            host = self.config.get("mqtt_host", "core-mosquitto")
            port = self.config.get("mqtt_port", 1883)
            
            logger.info(f"Connecting to MQTT broker at {host}:{port}")
            self.mqtt_client.connect(host, port, 60)
            self.mqtt_client.loop_start()
            
            # Wait for connection
            timeout = 10
            while not self.mqtt_connected and timeout > 0:
                time.sleep(1)
                timeout -= 1
            
            return self.mqtt_connected
            
        except Exception as e:
            logger.error(f"Failed to connect to MQTT: {e}")
            return False

    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            self.mqtt_connected = True
        else:
            logger.error(f"MQTT connection failed with code: {rc}")
            self.mqtt_connected = False

    def _on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        logger.warning(f"Disconnected from MQTT broker (rc: {rc})")
        self.mqtt_connected = False

    def publish_discovery(self):
        """Publish MQTT Discovery configurations for all sensors"""
        logger.info("Publishing MQTT Discovery configurations")
        
        for sensor_id, (name, unit, device_class, state_class, icon) in SENSORS.items():
            # Determine unit
            if unit is None and sensor_id in ["temperature", "feels_like"]:
                unit = self.get_unit_symbol("temperature")
            elif unit is None and sensor_id == "wind_speed":
                unit = self.get_unit_symbol("wind_speed")
            
            # Build discovery payload
            config_payload = {
                "name": f"OpenWeatherMap {name}",
                "unique_id": f"owm_{sensor_id}",
                "state_topic": f"openweathermap/sensor/{sensor_id}/state",
                "device": DEVICE_INFO,
                "icon": icon,
            }
            
            if unit:
                config_payload["unit_of_measurement"] = unit
            if device_class:
                config_payload["device_class"] = device_class
            if state_class:
                config_payload["state_class"] = state_class
            
            # Publish discovery config
            discovery_topic = f"{DISCOVERY_PREFIX}/sensor/openweathermap/{sensor_id}/config"
            self.mqtt_client.publish(
                discovery_topic,
                json.dumps(config_payload),
                retain=True
            )
            
        logger.info("MQTT Discovery configurations published")

    def fetch_weather(self) -> Optional[Dict[str, Any]]:
        """Fetch weather data from OpenWeatherMap API"""
        try:
            params = {
                "appid": self.config["api_key"],
                "units": self.config.get("units", "metric"),
                "lang": self.config.get("language", "en"),
            }
            
            # Add location
            lat = self.config.get("latitude")
            lon = self.config.get("longitude")
            
            if lat and lon:
                params["lat"] = lat
                params["lon"] = lon
            else:
                logger.error("Latitude and longitude are required")
                return None
            
            response = requests.get(OWM_API_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Weather data received: {data}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch weather data: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from API: {e}")
            return None

    def parse_weather_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse weather data into sensor values"""
        sensors = {}
        
        # Main weather data
        main = data.get("main", {})
        sensors["temperature"] = main.get("temp")
        sensors["feels_like"] = main.get("feels_like")
        sensors["humidity"] = main.get("humidity")
        sensors["pressure"] = main.get("pressure")
        
        # Wind data
        wind = data.get("wind", {})
        sensors["wind_speed"] = wind.get("speed")
        sensors["wind_direction"] = wind.get("deg")
        
        # Clouds
        clouds = data.get("clouds", {})
        sensors["clouds"] = clouds.get("all")
        
        # Visibility
        sensors["visibility"] = data.get("visibility")
        
        # Weather condition
        weather = data.get("weather", [{}])[0]
        sensors["weather_condition"] = weather.get("main")
        sensors["weather_description"] = weather.get("description")
        
        # Sun times (convert to ISO format)
        sys_data = data.get("sys", {})
        sunrise = sys_data.get("sunrise")
        sunset = sys_data.get("sunset")
        
        if sunrise:
            from datetime import datetime, timezone
            sensors["sunrise"] = datetime.fromtimestamp(sunrise, tz=timezone.utc).isoformat()
        if sunset:
            from datetime import datetime, timezone
            sensors["sunset"] = datetime.fromtimestamp(sunset, tz=timezone.utc).isoformat()
        
        return sensors

    def publish_sensor_states(self, sensors: Dict[str, Any]):
        """Publish sensor state values to MQTT"""
        for sensor_id, value in sensors.items():
            if value is not None:
                state_topic = f"openweathermap/sensor/{sensor_id}/state"
                self.mqtt_client.publish(state_topic, str(value), retain=True)
        
        logger.info("Sensor states published")

    def run(self):
        """Main service loop"""
        logger.info("Starting OpenWeatherMap service")
        
        # Load configuration
        if not self.load_config():
            logger.error("Failed to load configuration, exiting")
            sys.exit(1)
        
        # Connect to MQTT
        if not self.connect_mqtt():
            logger.error("Failed to connect to MQTT, exiting")
            sys.exit(1)
        
        # Publish discovery configurations
        self.publish_discovery()
        
        # Main loop
        update_interval = self.config.get("update_interval", 600)
        last_update = 0
        
        while self.running:
            current_time = time.time()
            
            # Check if it's time to update
            if current_time - last_update >= update_interval:
                logger.info("Fetching weather data...")
                
                weather_data = self.fetch_weather()
                if weather_data:
                    sensors = self.parse_weather_data(weather_data)
                    self.publish_sensor_states(sensors)
                    last_update = current_time
                else:
                    logger.warning("Failed to fetch weather data, will retry")
            
            # Sleep for a bit
            time.sleep(10)
        
        # Cleanup
        logger.info("Shutting down...")
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        logger.info("Service stopped")


if __name__ == "__main__":
    service = WeatherService()
    service.run()