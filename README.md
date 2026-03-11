# Global Historical Weather Analytics API
A RESTful API providing analytics for given cities which covers the last 25 years, built with Django REST Framework.

## Introduction
This API stores and processes data collected between 1st January 2000 and the 31st December 2025. The data is sourced from Open-Meteo, and the user has the option to view the results of these different analyses filtered by some city:
1. Monthly Analytics
2. Yearly Analytics
3. Extreme Analytics over the entire time period
4. The Köppen Classification of a city, using the data collected

The cities chosen for the API cover a wide range of climates for the Köppen classification system..

## Cities Covered
1. Yakutsk, Russia: One of the coldest inhabites cities on Earth, extreme continental cold
2. Reykjavik, Iceland: Represents the subpolar coeanic climate
3. London, United Kingdom: Temperate oceanic city
4. Cairo, Egypt: Hot desert
5. Mumbai, India: Tropical monsoon, representative of the South Asian monsoon climate
6. Singapore, Singapore: Tropical rainforest, an equitorial city-state with no seasons
7. Nairobi, Kenya: Subtropical highland
8. São Paulo, Brazil: Humid subtropical representative of the Southern Hemisphere
9. Calama, Chile: Cold desert, driest non-polar desert on Earth
10. McMurdo Station, Antarctica: A polar extreme located in Antarctica, one of the only places, with Greenland, to be given the Ice Cap classification, eternal winters and freezing temperatures

All continents covered except Australia, as Australia's main climates are already covered in the dataset.

## Tech Stack
- **Backend:** Django 6.0.2 + Django REST Framework 3.16.1
- **Database:** SQLite
- **Authentication:** DRF Token Authentication
- **Documentation:** drf-spectacular (OpenAPI/Swagger)
- **Data Source:** Open-Meteo Historical Archive (https://open-meteo.com/)

## Setup Instructions
### Prerequisites
- Python 3.13.2
- pip

### Installation
1. Clone the repository:
```bash
git clone https://github.com/mattyluke/weather-api
cd weather-api/weather_api
```

2. Run migrations:
```bash
python manage.py migrate
python manage.py makemigrations
```

3. Populate the database with data:
```bash
python db_import.py
```

4. Run the development server:
```bash
python manage.py runserver
```

5. Visit the API:
```bash
http://localhost:8000/api/
```

## Key Endpoints
GET /api/cities                                         | Returns a list of all cities

GET /api/cities/{name}/analytics_extremes/              | Returns extreme days for each variable

GET /api/cities/{name}/analytics_yearly/{year}          | Returns analytics for each year for a city, optional year argument to filter for that year

GET /api/cities/{name}/analytics_monthly/{year}/{month} | Returns analytics for each month, optinal year and month argument to filter for that year and month

GET /api/cities/{name}/analytics_streaks/               | Returns longest streaks of wet or dry days for each city

GET /api/cities/{name}/koppen/                          | Returns the Köppen classification of a city, calculated using the data in the database
