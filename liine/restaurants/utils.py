import re
import datetime
from typing import List, Tuple, Union

from django.db.models import QuerySet

from restaurants.models import Restaurant, OperatingDay, OperatingHours

DAY_TO_NUMBER_MAPPING = {
  "Mon": 0,
  "Tues": 1,
  "Wed": 2,
  "Thu": 3,
  "Fri": 4,
  "Sat": 5,
  "Sun": 6
}

DAYS_RANGE = list(range(7))

def parse_days(hours_set: str) -> List[int]:
  """
  This Python function parses a string representing days of the week with hours and returns a list of
  corresponding day numbers.
  
  :param hours_set: a given string representing hours of operation for a restaurant. The function uses regular
  expressions to extract the day patterns from the input string and then processes them to determine
  the days the restaurant is open
  :type hours_set: str
  :return: a list of integers representing the days of the week.
  """
  days = []
  day_pattern = "[A-Za-z]+-[A-Za-z]+, [A-Za-z]+| [A-Za-z]+, [A-Za-z]+-[A-Za-z]+|[A-Za-z]+-[A-Za-z]+|[A-Za-z]{3,}"
  day_pattern_match = re.search(day_pattern, hours_set)
  day_pattern_found = hours_set[day_pattern_match.start():day_pattern_match.end()]

  if ',' in day_pattern_found:
    # we have non-consecutive days that share hours
    clauses = day_pattern_found.split(',')
    # separate them
    for clause in clauses:
      if '-' in clause:
        # find the start and end of the day range that shares common hours
        start_day, end_day = clause.split('-')
        # add them to the list of days the restaurant is open
        days.extend(DAYS_RANGE[DAY_TO_NUMBER_MAPPING[start_day]:DAY_TO_NUMBER_MAPPING[end_day] + 1])
      else:
        # it's just a single day, so add it
        days.append(DAY_TO_NUMBER_MAPPING[clause.strip()])
  else:
    if '-' in day_pattern_found:
      # this is a date range, do the date-range thing
        start_day, end_day = day_pattern_found.split('-')
        days.extend(DAYS_RANGE[DAY_TO_NUMBER_MAPPING[start_day]:DAY_TO_NUMBER_MAPPING[end_day] + 1])
    else:
      # should just be a single day, do the single day thing. 
      # There are no restaurants in the data set that meet this criteria
      # so this block should never be reached but cover our bases should the data set expand.
      days.append(DAY_TO_NUMBER_MAPPING[day_pattern_found])

  return days

def parse_time(hours_set: str) -> List[datetime.time]:
  """
  The function `parse_time` takes a string input representing a set of hours in various formats and
  returns a list of standardized time objects.
  
  :param hours_set: a given string representing hours of operation for a restaurant. The function uses regular
  expressions to extract the hours patterns from the input string and then processes them to determine
  the what hours the restaurant is open during the day.
  :type hours_set: str
  :return: The function `parse_time` is returning a list of `datetime.time` objects after parsing and
  standardizing the time format from the input `hours_set` string.
  """
  hours_pattern = "[0-9]+:[0-9]+ [a-z]{2,} - [0-9]+:[0-9]+ [a-z]{2,}|[0-9]+:[0-9]+ [a-z]{2,} - [0-9]+ [a-z]{2,}|[0-9]+ [a-z]{2,} - [0-9]+:[0-9]+ [a-z]{2,}|[0-9]+ [a-z]{2,} - [0-9]+ [a-z]{2,}"
  hours_pattern_match = re.search(hours_pattern, hours_set)
  hours_pattern_found = hours_set[hours_pattern_match.start():hours_pattern_match.end()]

  raw_hours = hours_pattern_found.split('-')

  raw_hours_stripped = [hour.strip() for hour in raw_hours]

  # standardize time format
  hours_massaged = []
  for raw_hours in raw_hours_stripped:
    if ':' in raw_hours:
      hours_massaged.append(raw_hours)
    else:
      if len(raw_hours) == 4:
        hours_massaged.append(raw_hours[:1] + ':00 ' + raw_hours[2:])
      if len(raw_hours) == 5:
        hours_massaged.append(raw_hours[:2] + ':00 ' + raw_hours[3:])

  return [datetime.datetime.strptime(hours, '%I:%M %p').time() for hours in hours_massaged]

def parse_day_and_hours(hours_set: str) -> Tuple[Union[int, datetime.time]]:
  opening_time, closing_time = parse_time(hours_set)

  days = parse_days(hours_set)

  return days, opening_time, closing_time

def add_to_db(name: str, days: List[int], opening_time: datetime.time, closing_time: datetime.time) -> None:
  restaurant, _ = Restaurant.objects.get_or_create(name=name)

  for day in days:
    operating_day = OperatingDay.objects.create(
      name=day,
      restaurant=restaurant
    )
    OperatingHours.objects.create(
      opening_time=opening_time,
      closing_time=closing_time,
      operating_day=operating_day
    )

def parse_row(row: str) -> None:
  """
  This function parses restaurant operating hours from a given row of data, accounting for cases where
  closing time extends into the next day.
  
  :param row: a row of data containing information about a restaurant's name and operating hours. 
  :type row: str
  """
  name = row['Restaurant Name']
  split_row = row['Hours'].split('/')
  if len(split_row) > 1:
    for hours_set in split_row:
      days, opening_time, closing_time = parse_day_and_hours(hours_set)
      # account for when the closing time is technically the next day, ex. midnight or 4 am
      # add a new OperatingDay to the set to account for this window of operation
      if closing_time < opening_time:
        if days[-1] + 1 != 6:
          # add an extra day to the list of days, unless open sunday as the next day loops back to monday
          days.append(days[-1] + 1)
          technical_closing_time = closing_time
          technical_opening_time = datetime.time(0, 0, 0)
          # window of service on the next day is from midnight until whatever in the am
          add_to_db(name, days, technical_opening_time, technical_closing_time)
        # since the operating window extends into the next day, close this day's operating window at 11:59
        closing_time = datetime.time(23, 59, 59, 999999)
      add_to_db(name, days, opening_time, closing_time)
  else:
    days, opening_time, closing_time = parse_day_and_hours(split_row[0])
    if closing_time < opening_time:
      if days[-1] + 1 != 6:
        # same as above
        days.append(days[-1] + 1)
        technical_closing_time = closing_time
        technical_opening_time = datetime.time(0, 0, 0)
        add_to_db(name, days, technical_opening_time, technical_closing_time)
    closing_time = datetime.time(23, 59, 59, 999999)
    add_to_db(name, days, opening_time, closing_time)


def execute_search(time_string: str) -> QuerySet:
  time_string = time_string.replace("'", '').replace('"', '')  # clean the string
  datetime_obj = datetime.datetime.strptime(time_string, '%Y-%m-%d %H:%M:%S.%f')
  time = datetime_obj.time()
  day = datetime_obj.weekday()

  return Restaurant.objects.filter(
    operatingday_set__name=day,
    operatingday_set__operatinghours_set__opening_time__lte=time,
    operatingday_set__operatinghours_set__closing_time__gte=time
    ).distinct()