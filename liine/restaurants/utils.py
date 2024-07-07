import re
import datetime

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

def parse_days(hours_set):
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

def parse_time(hours_set):
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

def parse_day_and_hours(hours_set):
  opening_time, closing_time = parse_time(hours_set)

  days = parse_days(hours_set)

  return days, opening_time, closing_time

def add_to_db(name, days, opening_time, closing_time):
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

def parse_row(row):
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