from django.db import models

class City(models.Model):
    name = models.CharField(max_length=30)
    longitude = models.FloatField()
    latitude = models.FloatField()
    country = models.CharField(max_length=30)

    class Meta:
        unique_together = ['name', 'country']

    def __str__(self):
        return f"{self.name}, {self.country}"

class Weather(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="weather_records")
    date = models.DateField()
    mintemp = models.FloatField()
    maxtemp = models.FloatField()
    wind_speed = models.FloatField()
    precipitation = models.FloatField()

    class Meta:
        unique_together = ['city', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.city.name}, {self.date}"