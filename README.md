# Weather App 🌤️

A beautiful, modern weather application built with Django and Material Design 3, powered by the Open-Meteo API.

## Features

- **🌍 Real-time Weather Data** - Current conditions, hourly and 7-day forecasts
- **🎨 Material Design 3** - Beautiful, responsive interface with smooth animations
- **📱 Personal History** - Browser-stored search history (no shared data)
- **⚡ Fast & Reliable** - Cached API responses with automatic retries
- **🔒 Privacy-First** - No user data stored in database

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install django openmeteo-requests requests-cache retry-requests pandas
   ```

2. **Run the app:**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

3. **Open browser:** `http://localhost:8000`

## Tech Stack

- **Backend:** Django 5.2
- **Weather API:** Open-Meteo (free, no API key required)
- **Frontend:** Material Design 3, Vanilla JavaScript
- **Storage:** Browser localStorage (user-specific history)
- **Caching:** requests-cache with 1-hour expiry

## Project Structure

```
DWeather/
├── DWeather/          # Django project configuration
│   ├── settings.py    # Main settings
│   ├── urls.py        # Main URL routing
│   └── wsgi.py        # WSGI configuration
├── weather/           # Weather Django app
│   ├── services.py    # Centralized weather API service
│   ├── views.py       # Request handlers
│   ├── models.py      # Optional cache model
│   └── urls.py        # App URL routing
├── templates/         # HTML templates
│   ├── base.html      # Base template
│   └── weather/       # App-specific templates
├── static/css/        # Material Design 3 styles
└── manage.py         # Django management
```

## No Configuration Required

The app works out of the box - no API keys, database setup, or configuration files needed!

## License

Open source - feel free to use and modify.
