import csv

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
              add_to_db(name, days, opening_time, closing_time)
          else:
            days, opening_time, closing_time = parse_day_and_hours(split_row[0])
            add_to_db(name, days, opening_time, closing_time)

    print('CSV loaded into database.')