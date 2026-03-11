from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import City, Weather
from .serializers import CitySerializer, WeatherSerializer
from django.db.models import Avg, Max, Min, Sum, StdDev, Count, Q
from django.db.models.functions import ExtractYear, ExtractMonth, Round
from .utils import calculate_koppen
from drf_spectacular.utils import extend_schema

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

    @extend_schema(description="Returns the hottest, coldest, wettest and windiest days ever recorded for a city")
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
    
    @extend_schema(description="Returns analytics such as maximum temperature, minimum temperature, total rainfall and standard deviation for all variables for a given year")
    @action(detail=True, methods=['get'])
    def analytics_yearly(self, request, pk=None, year=None):
        city = self.get_object()
        records = Weather.objects.filter(city=city)

        if not records.exists():
            return Response(
                {"error": "No weather data for this city"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if year:
            records = records.filter(date__year = year)
        
        yearly_records = (
            records
            .annotate(year=ExtractYear('date'))
            .values('year')
            .annotate(
                max_temp = Max('maxtemp'),
                min_temp = Min('mintemp'),
                total_rainfall = Sum('precipitation'),
                avg_wind_speed = Round(Avg('wind_speed'), 3),
                heavy_rain_days = Count('id', filter = Q(precipitation__gt = 25)),
                storm_days = Count('id', filter = Q(wind_speed__gt = 89)),
                precipitation_std_dev = Round(StdDev('precipitation'), 3),
                wind_speed_std_dev = Round(StdDev('wind_speed'), 3),
                wet_dry_ratio = Round((Count('id', filter = Q(precipitation__gt = 0)) * 1.0 / Count('id')), 3)
            )
            .order_by('year')
        )

        return Response({
            'city': city.name,
            'country' : city.country,
            'yearly_data' : list(yearly_records)
        })


    @extend_schema(description="Returns analytics such as maximum temperature, minimum temperature, total rainfall and standard deviation for all variables for a given year and month")
    @action(detail=True, methods=['get'])
    def analytics_monthly(self, request, pk=None, year=None, month=None):
        city = self.get_object()
        records = Weather.objects.filter(city=city)

        if not records.exists():
            return Response(
                {"error": "No weather data for this city"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if year:
            records = records.filter(date__year = year)

        if month:
            records = records.filter(date__month = month)
        
        monthly_records = (
            records
            .annotate(year=ExtractYear('date'),
                      month=ExtractMonth('date'))
            .values('year', 'month')
            .annotate(
                max_temp = Max('maxtemp'),
                min_temp = Min('mintemp'),
                total_rainfall = Sum('precipitation'),
                avg_wind_speed = Round(Avg('wind_speed'), 3),
                heavy_rain_days = Count('id', filter = Q(precipitation__gt = 25)),
                storm_days = Count('id', filter = Q(wind_speed__gt = 89)),
                max_temp_std_dev = Round(StdDev('maxtemp'), 3),
                min_temp_std_dev = Round(StdDev('mintemp'), 3),
                precipitation_std_dev = Round(StdDev('precipitation'), 3),
                wind_speed_std_dev = Round(StdDev('wind_speed'), 3),
                wet_dry_ratio = Round((Count('id', filter = Q(precipitation__gt = 0)) * 1.0 / Count('id')), 3)
            )
            .order_by('year', 'month')
        )

        return Response({
            'city': city.name,
            'country' : city.country,
            'monthly_data' : list(monthly_records)
        })
    
    @extend_schema(description="Returns the longest consecutive days with precipitation and longest consecutive days without precipitation for a given city across all recorded years")
    @action(detail=True, methods=['get'])
    def analytics_streaks(self, request, pk=None):
        city = self.get_object()
        records = Weather.objects.filter(city=city).order_by('date')

        if not records.exists():
            return Response(
                {"error": "No weather data for this city"},
                status= status.HTTP_404_NOT_FOUND
            )
        
        longest_dry = 0
        current_dry = 0
        longest_wet = 0
        current_wet = 0

        current_dry_start = None
        current_wet_start = None

        longest_dry_start = None
        longest_dry_end = None
        longest_wet_start = None
        longest_wet_end = None

        for record in records:
            if record.precipitation <= 1:
                if current_dry == 0:
                    current_dry_start = record.date
                
                current_dry += 1
                current_wet = 0
                current_wet_start = None

                if current_dry > longest_dry:
                    longest_dry = current_dry
                    longest_dry_start = current_dry_start
                    longest_dry_end = record.date
            
            else:
                if current_wet == 0:
                    current_wet_start = record.date
                
                current_wet += 1
                current_dry = 0
                current_dry_start = None

                if current_wet > longest_wet:
                    longest_wet = current_wet
                    longest_wet_start = current_wet_start
                    longest_wet_end = record.date

        return Response({
            "city": city.name,
            "country": city.country,
            "streaks": {
                "longest_dry_streak": {
                    "days": longest_dry,
                    "start": longest_dry_start,
                    "end": longest_dry_end
                },
                "longest_wet_streak": {
                    "days": longest_wet,
                    "start": longest_wet_start,
                    "end": longest_wet_end
                }
            }
        })

    @extend_schema(description="Returns the Köppen classification of a city using the recorded measurements")
    @action(detail=True, methods=['get'])
    def koppen(self, request, pk=None):
        city = self.get_object()
        records = Weather.objects.filter(city=city)

        if not records.exists():
            return Response({
                "error": "No weather data for this city"},
                status = status.HTTP_404_NOT_FOUND
            )
        
        classification = calculate_koppen(records)

        return Response({
            "city": city.name,
            "country": city.country,
            "koppen_code": classification['code'],
            "classification": classification['name'],
            "description": classification['description']
        })

class WeatherViewSet(viewsets.ModelViewSet):
    serializer_class = WeatherSerializer

    def get_queryset(self):
        return Weather.objects.filter(city_id=self.kwargs['city_pk'])
    
    def perform_create(self, serializer):
        city = City.objects.get(pk = self.kwargs['city_pk'])
        serializer.save(city=city)