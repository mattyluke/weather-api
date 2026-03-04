from django.db import models

class City(models.Model):
    longitude = models.FloatField()
    latitude = models.FloatField()
    country = models.CharField(max_length=30)

class Weather():
    city = models.CharField(max_length=30)
    start_date = models.DateField()
    end_date = models.DateField()
    temperature = models.FloatField()