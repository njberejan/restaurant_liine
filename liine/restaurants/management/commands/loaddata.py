import csv
import datetime

from django.db import transaction

from django.core.management.base import BaseCommand, CommandError

from restaurants.utils import parse_day_and_hours, add_to_db

class Command(BaseCommand):
  help = "Load restaurant hours data from restaurants.csv"

  def handle(self, *args, **kwargs):
    with open('restaurants/data/restaurants.csv', 'r') as file:
      reader = csv.DictReader(file)
      for row in reader:
        with transaction.atomic():
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

    print('CSV loaded into database.')