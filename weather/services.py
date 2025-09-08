"""
Weather service module using OpenMeteo SDK
Handles all weather API interactions with proper caching and retry logic
"""

import openmeteo_requests
import requests_cache
from retry_requests import retry
from datetime import datetime
import requests

class WeatherService:
    """Centralized weather service using OpenMeteo SDK"""

    def __init__(self):
        # Setup the Open-Meteo API client with cache and retry on error
        try:
            cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
            retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
            self.openmeteo = openmeteo_requests.Client(session=retry_session)
        except Exception as e:
            print(f"Failed to initialize OpenMeteo client: {e}")
            self.openmeteo = None

        # Weather code mappings
        self.weather_codes = {
            0: {"description": "Clear sky", "icon": "wb_sunny"},
            1: {"description": "Mainly clear", "icon": "wb_sunny"},
            2: {"description": "Partly cloudy", "icon": "partly_cloudy_day"},
            3: {"description": "Overcast", "icon": "cloud"},
            45: {"description": "Fog", "icon": "foggy"},
            48: {"description": "Depositing rime fog", "icon": "foggy"},
            51: {"description": "Light drizzle", "icon": "grain"},
            53: {"description": "Moderate drizzle", "icon": "grain"},
            55: {"description": "Dense drizzle", "icon": "grain"},
            61: {"description": "Slight rain", "icon": "rainy"},
            63: {"description": "Moderate rain", "icon": "rainy"},
            65: {"description": "Heavy rain", "icon": "rainy"},
            71: {"description": "Slight snow", "icon": "ac_unit"},
            73: {"description": "Moderate snow", "icon": "ac_unit"},
            75: {"description": "Heavy snow", "icon": "ac_unit"},
            80: {"description": "Slight rain showers", "icon": "rainy"},
            81: {"description": "Moderate rain showers", "icon": "rainy"},
            82: {"description": "Violent rain showers", "icon": "rainy"},
            95: {"description": "Thunderstorm", "icon": "thunderstorm"},
            96: {"description": "Thunderstorm with hail", "icon": "thunderstorm"},
            99: {"description": "Thunderstorm with heavy hail", "icon": "thunderstorm"},
        }

    def get_location_data(self, city_name):
        """Get location coordinates using OpenMeteo Geocoding API"""
        try:
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('results'):
                result = data['results'][0]
                return {
                    'name': result.get('name'),
                    'latitude': result.get('latitude'),
                    'longitude': result.get('longitude'),
                    'country': result.get('country'),
                    'timezone': result.get('timezone', 'UTC')
                }
        except Exception as e:
            print(f"Error fetching location data: {e}")

        return None

    def get_weather_data(self, latitude, longitude):
        """Get weather data using OpenMeteo API"""
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'current': [
                    'temperature_2m', 'apparent_temperature', 'relative_humidity_2m',
                    'weather_code', 'surface_pressure', 'wind_speed_10m',
                    'wind_direction_10m', 'uv_index'
                ],
                'hourly': ['temperature_2m', 'weather_code', 'wind_speed_10m'],
                'daily': [
                    'temperature_2m_max', 'temperature_2m_min', 'weather_code',
                    'precipitation_sum', 'wind_speed_10m_max'
                ],
                'timezone': 'auto',
                'forecast_days': 7
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None

    def get_weather_info(self, weather_code):
        """Get weather description and icon for a weather code"""
        return self.weather_codes.get(int(weather_code), self.weather_codes[0])

    def get_weather_icon_name(self, weather_code):
        """Get Material Design icon name for weather code"""
        return self.get_weather_info(weather_code)['icon']

    def format_wind_direction(self, degrees):
        """Convert wind direction degrees to compass direction"""
        if degrees is None:
            return "N/A"

        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                     'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

        direction_index = int(round(degrees / 22.5) % 16)
        return f"{degrees}° ({directions[direction_index]})"

    def process_hourly_forecast(self, hourly_data, max_hours=24):
        """Process hourly forecast data"""
        if not hourly_data or 'time' not in hourly_data:
            return []

        forecast_items = []
        for i in range(min(len(hourly_data['time']), max_hours)):
            try:
                time_str = hourly_data['time'][i]
                dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))

                item = {
                    'time': dt.strftime('%H:%M'),
                    'temperature': round(hourly_data['temperature_2m'][i]) if i < len(hourly_data['temperature_2m']) else 0,
                    'weather_code': hourly_data['weather_code'][i] if i < len(hourly_data['weather_code']) else 0,
                    'wind_speed': round(hourly_data['wind_speed_10m'][i]) if i < len(hourly_data['wind_speed_10m']) else 0,
                    'icon': self.get_weather_icon_name(hourly_data['weather_code'][i] if i < len(hourly_data['weather_code']) else 0)
                }
                forecast_items.append(item)
            except (IndexError, KeyError, TypeError, ValueError):
                continue

        return forecast_items

    def process_daily_forecast(self, daily_data, max_days=7):
        """Process daily forecast data"""
        if not daily_data or 'time' not in daily_data:
            return []

        forecast_items = []
        for i in range(min(len(daily_data['time']), max_days)):
            try:
                date_str = daily_data['time'][i]
                if i == 0:
                    date_display = "Today"
                elif i == 1:
                    date_display = "Tomorrow"
                else:
                    dt = datetime.fromisoformat(date_str)
                    date_display = dt.strftime('%m/%d')

                precipitation = daily_data['precipitation_sum'][i] if i < len(daily_data['precipitation_sum']) else 0

                item = {
                    'date': date_display,
                    'temp_max': round(daily_data['temperature_2m_max'][i]) if i < len(daily_data['temperature_2m_max']) else 0,
                    'temp_min': round(daily_data['temperature_2m_min'][i]) if i < len(daily_data['temperature_2m_min']) else 0,
                    'weather_code': daily_data['weather_code'][i] if i < len(daily_data['weather_code']) else 0,
                    'precipitation': precipitation,
                    'wind_speed': round(daily_data['wind_speed_10m_max'][i]) if i < len(daily_data['wind_speed_10m_max']) else 0,
                    'icon': self.get_weather_icon_name(daily_data['weather_code'][i] if i < len(daily_data['weather_code']) else 0),
                    'precipitation_text': "No rain" if precipitation <= 0 else f"{precipitation:.1f}mm"
                }
                forecast_items.append(item)
            except (IndexError, KeyError, TypeError, ValueError):
                continue

        return forecast_items
