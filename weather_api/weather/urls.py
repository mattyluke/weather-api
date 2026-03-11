from rest_framework_nested import routers
from django.urls import path, include
from . import views

router = routers.DefaultRouter()
router.register(r"cities", views.CityViewSet)

cities_router = routers.NestedDefaultRouter(router, r'cities', lookup='city')
cities_router.register(r'weather', views.WeatherViewSet, basename='city-weather')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(cities_router.urls)),

    # Yearly
    path('cities/<str:pk>/analytics_yearly/',
         views.CityViewSet.as_view({'get': 'analytics_yearly'})),
    path('cities/<str:pk>/analytics_yearly/<int:year>',
         views.CityViewSet.as_view({'get': 'analytics_yearly'})),

    # Monthly
    path('cities/<str:pk>/analytics_monthly/',
         views.CityViewSet.as_view({'get': 'analytics_monthly'})),
    path('cities/<str:pk>/analytics_monthly/<int:year>',
         views.CityViewSet.as_view({'get': 'analytics_monthly'})),
    path('cities/<str:pk>/analytics_monthly/<int:year>/<int:month>',
         views.CityViewSet.as_view({'get': 'analytics_monthly'}))
]