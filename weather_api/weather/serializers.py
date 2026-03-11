from rest_framework import serializers
from .models import City, Weather

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'longitude', 'latitude', 'country']

class WeatherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weather
        fields = ['id', 'date', 'maxtemp', 'mintemp', 'precipitation','wind_speed', 'city_id']