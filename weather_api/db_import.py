import os
import time
import django
import requests

Cities = [
    {"name": "Yakutsk", "longitude": 129.73, "latitude": 62.04, "country": "RU"},
    {"name": "Reykjavik", "longitude": -21.82, "latitude": 64.13, "country": "IS"},
    {"name": "London", "longitude": -0.13, "latitude": 51.51, "country": "GB"},
    {"name": "Cairo", "longitude": 31.24, "latitude": 30.04, "country": "EG"},
    {"name": "Mumbai", "longitude": 72.88, "latitude": 19.08, "country": "IN"},
    {"name": "Singapore", "longitude": 103.82, "latitude": 1.35, "country": "SG"},
    {"name": "Nairobi", "longitude": 36.82, "latitude": -1.29, "country": "KE"},
    {"name": "São Paulo", "longitude": -46.63, "latitude": -23.55, "country": "BR"},
    {"name": "Calama", "longitude": -68.93, "latitude": -22.46, "country": "CL"},
    {"name": "McMurdo", "longitude": 166.67, "latitude": -77.85, "country": "AQ"}
]

def fetch_weather(longitude, latitude):
    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "longitude": longitude,
        "latitude": latitude,
        "daily": [
            "temperature_2m_min",
            "temperature_2m_max",
            "wind_speed_10m_max",
            "precipitation_sum"
        ],
        "start_date": "2000-01-01",
        "end_date": "2025-12-31"
    }

    print("...Calling Open-Meteo API...")
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print(f"API call failed with status {response.status_code}")
        return None
    
    return response.json()


def import_city(city_data):
    from weather.models import City

    print(f"...Importing {city_data['name']}, {city_data['country']}...")

    city, created = City.objects.get_or_create(
        name=city_data["name"],
        country=city_data["country"],
        defaults={
            "longitude": city_data['longitude'],
            "latitude": city_data['latitude']
        }
    )

    if created:
        print(f"...Created {city.name}...")
    else:
        print(f"...Found {city.name} already existing...")

    return city


def import_weather_records(city_obj):
    from weather.models import Weather

    data = fetch_weather(city_obj.longitude, city_obj.latitude)

    if not data:
        print(f"...API Error while importing {city_obj.name}...")
        return

    daily = data["daily"]
    dates = daily["time"]

    total = len(dates)

    records_created = 0

    print(f"...Processing {total} days of weather stats...")

    for i, date in enumerate(dates):
        temp_max = daily["temperature_2m_max"][i]
        temp_min = daily["temperature_2m_min"][i]
        wind_speed = daily["wind_speed_10m_max"][i]
        precipitation = daily["precipitation_sum"][i]

        _, created = Weather.objects.get_or_create(
            city=city_obj,
            date=date,
            defaults={
                "maxtemp": temp_max,
                "mintemp": temp_min,
                "wind_speed": wind_speed,
                "precipitation": precipitation
            }
        )

        if created:
            records_created += 1

    print(f"...Created {records_created} records for {city_obj.name}...")


if __name__ == "__main__":

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weather_api.settings")
    django.setup()

    for city in Cities:
        city_obj = import_city(city)
        import_weather_records(city_obj)
        time.sleep(5)

    print("Import complete")