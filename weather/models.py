from django.db import models

# Simple model for potential future use - no more storing user data in shared DB
class WeatherCache(models.Model):
    """Optional cache model for server-side caching only"""
    location_key = models.CharField(max_length=100, unique=True)
    cache_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'weather_cache'

    def __str__(self):
        return f"Cache for {self.location_key}"
