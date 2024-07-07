from django.db import models

class Restaurant(models.Model):
  name = models.CharField(max_length=30, null=False, blank=False, unique=True)


class OperatingDay(models.Model):
  class Name(models.TextChoices):
    MONDAY = 0, "Monday"
    TUESDAY = 1, "Tuesday"
    WEDNESDAY = 2, "Wednesday"
    THURSDAY = 3, "Thursday"
    FRIDAY = 4, "Friday"
    SATURDAY = 5, "Saturday"
    SUNDAY = 6, "Sunday"

  name = models.CharField(choices=Name.choices, max_length=1)
  restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="operatingday_set", blank=True, null=True)


class OperatingHours(models.Model):
  opening_time = models.TimeField(auto_now=False, auto_now_add=False, null=False, blank=False)
  closing_time = models.TimeField(auto_now=False, auto_now_add=False, null=False, blank=False)
  operating_day = models.ForeignKey(OperatingDay, on_delete=models.CASCADE, related_name="operatinghours_set", null=False, blank=False)
