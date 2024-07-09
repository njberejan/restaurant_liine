import csv

from django.db import transaction

from django.core.management.base import BaseCommand

from restaurants.utils import parse_row

class Command(BaseCommand):
  help = "Load restaurant hours data from restaurants.csv"

  def add_arguments(self, parser):
    parser.add_argument(
        "--local",
        action="store_true",
        help="Run to seed database locally outside of the docker container",
    )

  def handle(self, *args, **options):

    file_location = '/app/liine/restaurants/data/restaurants.csv'

    if options['local']:
      file_location = 'restaurants/data/restaurants.csv'

    with open(file_location, 'r') as file:
      reader = csv.DictReader(file)
      for row in reader:
        with transaction.atomic():
          parse_row(row)

    print('CSV loaded into database.')