import typing as t

from django.shortcuts import render
from django.http import HttpResponseBadRequest, HttpRequest, HttpResponse

from restaurants.forms import DatetimeStringForm
from restaurants.utils import execute_search

def home(request: HttpRequest) -> HttpResponse:
    context = {"form": DatetimeStringForm()}
    return render(request, "restaurants/home.html", context)

def search(request: HttpRequest) -> t.Union[HttpResponse, HttpResponseBadRequest]:
  """
  The function takes a HttpRequest object, extracts a timestamp from the request parameters, executes
  a search based on the timestamp, and returns the search results in a rendered HTML template.

  :param request: The `request` parameter is of type `HttpRequest`
  :type request: HttpRequest
  :return: The function `search` is returning either an `HttpResponse` object or an
  `HttpResponseBadRequest` object. If the `time_string` is not provided in the request or if an error
  occurs during the search execution, it will return an `HttpResponseBadRequest` with an appropriate
  message. Otherwise, it will return a rendered HTML template with the search results.
  """
  time_string = request.GET.get("timestamp", None)
  if not time_string:
    return HttpResponseBadRequest('No input provided.')
  try:
    restaurants = execute_search(time_string)
  except ValueError as e:
    return HttpResponseBadRequest(str(e))
  return render(request, "restaurants/results.html", {"restaurants": restaurants})

