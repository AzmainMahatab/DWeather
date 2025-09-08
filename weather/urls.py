from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('forecast/<str:city>/', views.forecast, name='forecast'),
]
