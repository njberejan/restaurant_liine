import csv

from django.db import transaction

from django.core.management.base import BaseCommand

from restaurants.utils import parse_row

class Command(BaseCommand):
  help = "Load restaurant hours data from restaurants.csv"

  def handle(self, *args, **kwargs):
    with open('restaurants/data/restaurants.csv', 'r') as file:
      reader = csv.DictReader(file)
      for row in reader:
        with transaction.atomic():
          parse_row(row)

    print('CSV loaded into database.')