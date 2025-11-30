# Home Assistant Add-on: OpenWeatherMap

## Configuration

### Required Configuration

```yaml
api_key: "your-openweathermap-api-key"
latitude: "51.5074"
longitude: "-0.1278"
```

### Full Configuration Example

```yaml
api_key: "your-openweathermap-api-key"
latitude: "51.5074"
longitude: "-0.1278"
units: "metric"
language: "en"
update_interval: 600
mqtt_host: "core-mosquitto"
mqtt_port: 1883
mqtt_username: "mqtt_user"
mqtt_password: "mqtt_password"
```

### Option Descriptions

#### `api_key` (required)

Your OpenWeatherMap API key. You can get a free API key by:

1. Creating an account at [openweathermap.org](https://openweathermap.org/)
2. Going to your [API keys page](https://home.openweathermap.org/api_keys)
3. Generating a new API key

The free tier allows 1,000 API calls per day, which is more than enough for typical use.

#### `latitude` (required)

The latitude of the location for weather data. Use decimal degrees format (e.g., "51.5074" for London).

#### `longitude` (required)

The longitude of the location for weather data. Use decimal degrees format (e.g., "-0.1278" for London).

#### `units` (optional, default: "metric")

The unit system for temperature and wind speed:

| Value | Temperature | Wind Speed |
|-------|-------------|------------|
| `metric` | Celsius (°C) | meters/second (m/s) |
| `imperial` | Fahrenheit (°F) | miles/hour (mph) |
| `standard` | Kelvin (K) | meters/second (m/s) |

#### `language` (optional, default: "en")

Language code for weather descriptions. Supported languages include:

- `en` - English
- `de` - German
- `fr` - French
- `es` - Spanish
- `it` - Italian
- `pt` - Portuguese
- `ru` - Russian
- `ja` - Japanese
- `zh_cn` - Chinese Simplified

See [OpenWeatherMap documentation](https://openweathermap.org/current#multi) for the full list.

#### `update_interval` (optional, default: 600)

How often to fetch new weather data, in seconds. Valid range is 60-3600 (1-60 minutes).

**Note**: The free OpenWeatherMap API tier allows 1,000 calls per day. With the default 10-minute interval, you'll use approximately 144 calls per day.

#### `mqtt_host` (optional, default: "core-mosquitto")

The hostname of your MQTT broker. If you're using the Mosquitto add-on, the default value works automatically.

#### `mqtt_port` (optional, default: 1883)

The port number of your MQTT broker.

#### `mqtt_username` (optional)

Username for MQTT authentication. Leave empty if your broker doesn't require authentication.

#### `mqtt_password` (optional)

Password for MQTT authentication. Leave empty if your broker doesn't require authentication.

## MQTT Topics

The add-on publishes to the following MQTT topics:

### Discovery Topics

Discovery configurations are published to:
```
homeassistant/sensor/openweathermap/{sensor_id}/config
```

### State Topics

Sensor values are published to:
```
openweathermap/sensor/{sensor_id}/state
```

## Sensors

The following sensors are created automatically in Home Assistant:

| Entity ID | Description | Unit |
|-----------|-------------|------|
| `sensor.openweathermap_temperature` | Current temperature | °C/°F/K |
| `sensor.openweathermap_feels_like` | Feels like temperature | °C/°F/K |
| `sensor.openweathermap_humidity` | Relative humidity | % |
| `sensor.openweathermap_pressure` | Atmospheric pressure | hPa |
| `sensor.openweathermap_wind_speed` | Wind speed | m/s or mph |
| `sensor.openweathermap_wind_direction` | Wind direction | ° |
| `sensor.openweathermap_clouds` | Cloud coverage | % |
| `sensor.openweathermap_visibility` | Visibility | m |
| `sensor.openweathermap_condition` | Weather condition | - |
| `sensor.openweathermap_description` | Weather description | - |
| `sensor.openweathermap_sunrise` | Sunrise time | timestamp |
| `sensor.openweathermap_sunset` | Sunset time | timestamp |

## Troubleshooting

### No sensors appearing

1. Check that the MQTT broker is running
2. Verify your API key is correct
3. Check the add-on logs for errors

### API errors

- **401 Unauthorized**: Your API key is invalid or not yet activated (new keys can take a few hours)
- **429 Too Many Requests**: You've exceeded your API rate limit

### MQTT connection errors

1. Verify the MQTT broker hostname and port
2. Check if authentication is required
3. Ensure the Mosquitto add-on is running

## Support

For issues and feature requests, please visit the [GitHub repository](https://github.com/ihuf/addon).