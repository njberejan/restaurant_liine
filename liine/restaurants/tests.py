import datetime
from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse

from restaurants.utils import parse_days, parse_time, parse_day_and_hours, parse_row

class UtilsTestCase(TestCase):

  def setUp(self):
    self.row = {
      "Restaurant Name": "Bonchon",
      "Hours": "Mon-Wed 5 pm - 12:30 am / Thu-Fri 5 pm - 1:30 am / Sat 3 pm - 1:30 am / Sun 3 pm - 11:30 pm"
    }
    self.hours_sets = [
      "Mon-Wed 5 pm - 12:30 am",
      "Thu-Fri 5 pm - 1:30 am",
      "Sat 3 pm - 1:30 am",
      "Sun 3 pm - 11:30 pm"
    ]
    self.expected_results = {
      "days": {
        "Mon-Wed 5 pm - 12:30 am": [0, 1, 2],
        "Thu-Fri 5 pm - 1:30 am": [3, 4],
        "Sat 3 pm - 1:30 am": [5],
        "Sun 3 pm - 11:30 pm": [6]
      },
      "hours": {
        "Mon-Wed 5 pm - 12:30 am": {
          "opening_time": datetime.time(17, 0, 0, 0),
          "closing_time": datetime.time(0, 30, 0 , 0)
        },
        "Thu-Fri 5 pm - 1:30 am": {
          "opening_time": datetime.time(17, 0, 0, 0),
          "closing_time": datetime.time(1, 30, 0 , 0)
        },
        "Sat 3 pm - 1:30 am": {
          "opening_time": datetime.time(15, 0, 0, 0),
          "closing_time": datetime.time(1, 30, 0, 0)
        },
        "Sun 3 pm - 11:30 pm": {
          "opening_time": datetime.time(15, 0, 0, 0),
          "closing_time": datetime.time(23, 30, 0, 0)
        }
      }
    }

  def test_parse_days_returns_expected(self):
    for hours_set in self.hours_sets:
      expected = self.expected_results['days'][hours_set]
      actual = parse_days(hours_set)
      self.assertEqual(expected, actual)

  def test_parse_time_returns_expected(self):
    for hours_set in self.hours_sets:
      expected_opening = self.expected_results['hours'][hours_set]['opening_time']
      expected_closing = self.expected_results['hours'][hours_set]['closing_time']
      actual_opening, actual_closing = parse_time(hours_set)
      self.assertEqual(expected_opening, actual_opening)
      self.assertEqual(expected_closing, actual_closing)

  def test_parse_day_and_hours_returns_expected(self):
    for hours_set in self.hours_sets:
      actual_days, actual_opening_time, actual_closing_time = parse_day_and_hours(hours_set)
      self.assertEqual(self.expected_results['days'][hours_set], actual_days)
      self.assertEqual(self.expected_results['hours'][hours_set]['opening_time'], actual_opening_time)
      self.assertEqual(self.expected_results['hours'][hours_set]['closing_time'], actual_closing_time)

  @patch('restaurants.utils.add_to_db')
  def test_parse_row_raises_no_errors(self, mock_add_to_db):
    parse_row(self.row)
    assert mock_add_to_db.called

  @patch('restaurants.utils.add_to_db')
  def test_parse_row_raises_errors_with_bad_data(self, mock_add_to_db):
    with self.assertRaises(AttributeError):
      parse_row(
        {
          "Restaurant Name": "Cary Noodle Blvd",
          "Hours": "M-F 11AM - 8PM"
          }
      )
    assert not mock_add_to_db.called
    
class ViewsTestCase(TestCase):
  
  def setUp(self):
    self.client = Client()
    self.test_data_set = [
      {
        "Restaurant Name": "Culvers",
        "Hours": "Mon-Wed 5 pm - 12:30 am / Thu-Fri 5 pm - 1:30 am / Sat 3 pm - 1:30 am / Sun 3 pm - 11:30 pm"
      },
      {
        "Restaurant Name": "Cook Out",
        "Hours": "	Mon-Sun 11 am - 4 am"
      },
      {
        "Restaurant Name": "Waffle House",
        "Hours": "	Mon-Sun 12 am - 12 am"
      },
    ]
    for data in self.test_data_set:
      parse_row(data)

  def test_home_view(self):
    response = self.client.get('/')
    self.assertEqual(200, response.status_code)
    self.assertIn(b'What restaurants near Raleigh are open?', response.content)

  def test_search_view(self):
    response = self.client.get('/search/', {"timestamp": "2024-07-07 00:00:00.0"})
    self.assertEqual(200, response.status_code)
    self.assertIn(b'Waffle House', response.content)
    self.assertIn(b'Cook Out', response.content)