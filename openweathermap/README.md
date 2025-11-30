# Home Assistant Add-on: OpenWeatherMap

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

Fetch weather data from OpenWeatherMap and publish to Home Assistant via MQTT Discovery.

## About

This add-on fetches current weather data from the OpenWeatherMap API and automatically creates sensors in Home Assistant using MQTT Discovery. No manual sensor configuration required!

### Features

- **Automatic sensor creation** via MQTT Discovery
- **12 weather sensors** including temperature, humidity, pressure, wind, and more
- **Configurable update interval** (1-60 minutes)
- **Multiple unit systems** (metric, imperial, standard)
- **Multi-language support** for weather descriptions

### Sensors Created

| Sensor | Description |
|--------|-------------|
| Temperature | Current temperature |
| Feels Like | Apparent temperature |
| Humidity | Relative humidity percentage |
| Pressure | Atmospheric pressure |
| Wind Speed | Current wind speed |
| Wind Direction | Wind direction in degrees |
| Cloud Coverage | Cloud coverage percentage |
| Visibility | Visibility distance |
| Condition | Weather condition (Clear, Clouds, Rain, etc.) |
| Description | Detailed weather description |
| Sunrise | Today's sunrise time |
| Sunset | Today's sunset time |

## Prerequisites

1. **MQTT Broker**: You need an MQTT broker running. The [Mosquitto broker add-on](https://github.com/home-assistant/addons/tree/master/mosquitto) is recommended.
2. **OpenWeatherMap API Key**: Get a free API key at [openweathermap.org](https://openweathermap.org/api)

## Installation

1. Add this repository to your Home Assistant add-on store
2. Install the "OpenWeatherMap" add-on
3. Configure the add-on with your API key and location
4. Start the add-on

## Configuration

See the [Documentation](DOCS.md) for full configuration details.

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg