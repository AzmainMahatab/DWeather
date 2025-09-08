from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json
from .services import WeatherService

# Initialize the weather service once
weather_service = WeatherService()

def index(request):
    """Home page view - no more database queries for recent locations"""
    context = {
        'title': 'Weather App'
    }
    return render(request, 'weather/index.html', context)

@csrf_exempt
def search(request):
    """Search for a city and return weather data"""
    if request.method == 'POST':
        city_name = request.POST.get('city', '').strip()
        
        if not city_name:
            messages.error(request, 'Please enter a city name')
            return render(request, 'weather/index.html')
        
        # Get location data using centralized service
        location_data = weather_service.get_location_data(city_name)
        if not location_data:
            messages.error(request, f'City "{city_name}" not found. Please try again.')
            return render(request, 'weather/index.html')
        
        # Get weather data using centralized service
        weather_data = weather_service.get_weather_data(
            location_data['latitude'],
            location_data['longitude']
        )
        if not weather_data:
            messages.error(request, 'Unable to fetch weather data. Please try again.')
            return render(request, 'weather/index.html')
        
        # Process current weather using service
        current = weather_data.get('current', {})
        weather_code = current.get('weather_code', 0)
        weather_info = weather_service.get_weather_info(weather_code)

        # Process forecast data using service methods
        hourly_forecast = weather_service.process_hourly_forecast(weather_data.get('hourly', {}))
        daily_forecast = weather_service.process_daily_forecast(weather_data.get('daily', {}))

        # Prepare location data for frontend localStorage
        location_for_storage = {
            'name': location_data['name'],
            'country': location_data['country'],
            'latitude': location_data['latitude'],
            'longitude': location_data['longitude'],
            'searched_at': None  # Will be set by JavaScript
        }

        context = {
            'location': location_data,
            'current_weather': current,
            'weather_info': weather_info,
            'hourly_forecast': hourly_forecast,
            'daily_forecast': daily_forecast,
            'wind_direction_text': weather_service.format_wind_direction(current.get('wind_direction_10m')),
            'weather_icon': weather_service.get_weather_icon_name(weather_code),
            'location_json': json.dumps(location_for_storage),  # For localStorage
        }
        
        return render(request, 'weather/weather_detail.html', context)
    
    return render(request, 'weather/index.html')

def forecast(request, city):
    """Display weather forecast for a specific city"""
    try:
        # Since we don't store in DB, we need to search again
        location_data = weather_service.get_location_data(city)
        if not location_data:
            messages.error(request, f'City "{city}" not found. Please try again.')
            return render(request, 'weather/index.html')
        
        # Get fresh weather data using service
        weather_data = weather_service.get_weather_data(
            location_data['latitude'],
            location_data['longitude']
        )
        if not weather_data:
            messages.error(request, 'Unable to fetch weather data. Please try again.')
            return render(request, 'weather/index.html')
        
        # Process weather data using service
        current = weather_data.get('current', {})
        weather_code = current.get('weather_code', 0)
        weather_info = weather_service.get_weather_info(weather_code)

        # Process forecast data using service methods
        hourly_forecast = weather_service.process_hourly_forecast(weather_data.get('hourly', {}))
        daily_forecast = weather_service.process_daily_forecast(weather_data.get('daily', {}))

        # Prepare location data for frontend localStorage
        location_for_storage = {
            'name': location_data['name'],
            'country': location_data['country'],
            'latitude': location_data['latitude'],
            'longitude': location_data['longitude'],
            'searched_at': None  # Will be set by JavaScript
        }

        context = {
            'location': location_data,
            'current_weather': current,
            'weather_info': weather_info,
            'hourly_forecast': hourly_forecast,
            'daily_forecast': daily_forecast,
            'wind_direction_text': weather_service.format_wind_direction(current.get('wind_direction_10m')),
            'weather_icon': weather_service.get_weather_icon_name(weather_code),
            'location_json': json.dumps(location_for_storage),
        }
        
        return render(request, 'weather/weather_detail.html', context)
    
    except Exception as e:
        messages.error(request, 'An error occurred while fetching weather data.')
        return render(request, 'weather/index.html')

@csrf_exempt
def get_recent_locations(request):
    """API endpoint to get recent locations from browser localStorage"""
    if request.method == 'GET':
        # This will be handled by JavaScript on the frontend
        # No server-side storage needed
        return JsonResponse({'message': 'Use localStorage on frontend'})

    return JsonResponse({'error': 'Method not allowed'}, status=405)
