from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets
from .models import City, Weather
from .serializers import CitySerializer, WeatherSerializer

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class WeatherViewSet(viewsets.ModelViewSet):
    serializer_class = WeatherSerializer

    def get_queryset(self):
        return Weather.objects.filter(city_id=self.kwargs['city_pk'])
    
    def perform_create(self, serializer):
        city = City.objects.get(pk = self.kwargs['city_pk'])
        serializer.save(city=city)