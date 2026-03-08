from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import City, Weather
from .serializers import CitySerializer, WeatherSerializer
from django.db.models import Avg, Max, Min, Sum, StdDev, Count, Q
from django.db.models.functions import ExtractYear, ExtractMonth

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def get_object(self):
        pk = self.kwargs['pk']

        cities = City.objects.filter(name__iexact=pk)
        if cities:
            self.check_object_permissions(self.request, cities.first())
            return cities.first()
        return super().get_object()

    @action(detail=True, methods=['get'])
    def analytics_extremes(self, request, pk=None):
        city = self.get_object()
        records = Weather.objects.filter(city=city)

        if not records.exists():
            return Response(
                {"error": "No weather data for this city"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        hottest = records.order_by('-maxtemp').first()
        coldest = records.order_by('mintemp').first()
        wettest = records.order_by('-precipitation').first()
        windiest = records.order_by('-wind_speed').first()

        return Response({
            "city": city.name,
            "country": city.country,
            "extremes": {
                "hottest_day": {
                    "date": hottest.date,
                    "temp": hottest.maxtemp
                },
                "coldest_day": {
                    "date": coldest.date,
                    "temp": coldest.mintemp
                },
                "wettest_day": {
                    "date": wettest.date,
                    "precipitation": wettest.precipitation
                },
                "windiest_day": {
                    "date": windiest.date,
                    "wind_speed": windiest.wind_speed
                }
            }
        })

    @action(detail=True, methods=['get'])
    def analytics_yearly(self, request, pk=None):
        city = self.get_object()
        records = Weather.objects.filter(city=city)

        if not records.exists():
            return Response(
                {"error": "No weather data for this city"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        yearly_records = (
            records
            .annotate(year=ExtractYear('date'))
            .values('year')
            .annotate(
                max_temp = Max('maxtemp'),
                min_temp = Min('mintemp'),
                total_rainfall = Sum('precipitation'),
                avg_wind_speed = Avg('wind_speed'),
                heavy_rain_days = Count('id', filter = Q(precipitation__gt = 25)),
                storm_days = Count('id', filter = Q(wind_speed__gt = 89))
            )
            .order_by('year')
        )

        return Response({
            'city': city.name,
            'country' : city.country,
            'yearly_data' : list(yearly_records)
        })


    @action(detail=True, methods=['get'])
    def analytics_monthly(self, request, pk=None):
        pass

class WeatherViewSet(viewsets.ModelViewSet):
    serializer_class = WeatherSerializer

    def get_queryset(self):
        return Weather.objects.filter(city_id=self.kwargs['city_pk'])
    
    def perform_create(self, serializer):
        city = City.objects.get(pk = self.kwargs['city_pk'])
        serializer.save(city=city)