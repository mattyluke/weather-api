from rest_framework_nested import routers
from django.urls import path, include
from . import views

router = routers.DefaultRouter()
router.register(r"cities", views.CityViewSet)

cities_router = routers.NestedDefaultRouter(router, r'cities', lookup='city')
cities_router.register(r'weather', views.WeatherViewSet, basename='city-weather')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(cities_router.urls))
]