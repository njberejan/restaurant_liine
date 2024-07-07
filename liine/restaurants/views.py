import datetime

from django.shortcuts import render
from django.http import HttpResponseBadRequest

from restaurants.forms import DatetimeStringForm
from restaurants.models import Restaurant


def home(request):
    context = {"form": DatetimeStringForm()}
    return render(request, "restaurants/home.html", context)

def search(request):
  time_string = request.GET.get("timestamp", None)
  if not time_string:
    return HttpResponseBadRequest('No input provided.')
  else:
    time_string = time_string.replace("'", '').replace('"', '')
  try:
    datetime_obj = datetime.datetime.strptime(time_string, '%Y-%m-%d %H:%M:%S.%f')
  except ValueError as e:
    return HttpResponseBadRequest(str(e))
  time = datetime_obj.time()
  day = datetime_obj.weekday()

  restaurants = Restaurant.objects.filter(
    operatingday_set__name=day,
    operatingday_set__operatinghours_set__opening_time__lte=time,
    operatingday_set__operatinghours_set__closing_time__gte=time
    ).distinct()

  return render(request, "restaurants/results.html", {"restaurants": restaurants})

