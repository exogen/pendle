from datetime import datetime, time

from django.test import TestCase
from django.db.models.query import QuerySet

from pendle.catalog.models import Catalog, ReservationDuration, Period
from pendle.assets.models import Asset


class TestReservationDuration(TestCase):
    fixtures = ['test_catalog']

    def setUp(self):
        self.periods = Period.objects.all()
        self.durations = ReservationDuration.objects.in_bulk(range(11))

    def test_get_due_date_for_1_hour_exact_duration_is_1_hour_from_now(self):
        duration = self.durations[1]
        now = datetime(2011, 1, 1, 12, 0, 0)
        due_date = duration.get_due_date(now)
        self.assertEqual(due_date, datetime(2011, 1, 1, 13, 0, 0))

    def test_get_due_date_for_1_hour_end_duration_is_end_of_next_period_at_least_1_hour_from_now(self):
        duration = self.durations[2]
        now = datetime(2011, 1, 1, 12, 0, 0)
        due_date = duration.get_due_date(now, self.periods)
        self.assertEqual(due_date, datetime(2011, 1, 3, 17, 0, 0))

    def test_get_due_date_for_12_hour_exact_duration_is_12_hours_from_now(self):
        duration = self.durations[3]
        now = datetime(2011, 1, 1, 12, 0, 0)
        due_date = duration.get_due_date(now)
        self.assertEqual(due_date, datetime(2011, 1, 2, 0, 0, 0))

    def test_get_due_date_for_1_day_exact_duration_is_1_day_from_now(self):
        duration = self.durations[5]
        now = datetime(2011, 1, 1, 12, 0, 0)
        due_date = duration.get_due_date(now)
        self.assertEqual(due_date, datetime(2011, 1, 2, 12, 0, 0))

    def test_get_due_date_for_1_day_end_duration_is_end_of_next_period_at_least_1_day_from_now(self):
        duration = self.durations[6]
        now = datetime(2011, 1, 1, 12, 0, 0)
        due_date = duration.get_due_date(now, self.periods)
        self.assertEqual(due_date, datetime(2011, 1, 3, 17, 0, 0))

    def test_get_due_date_for_31_day_exact_duration_is_31_days_from_now(self):
        duration = self.durations[7]
        now = datetime(2011, 1, 1, 12, 0, 0)
        due_date = duration.get_due_date(now)
        self.assertEqual(due_date, datetime(2011, 2, 1, 12, 0, 0))

    def test_get_due_date_for_31_day_end_duration_is_end_of_next_period_at_least_31_days_from_now(self):
        duration = self.durations[8]
        now = datetime(2011, 1, 1, 12, 0, 0)
        due_date = duration.get_due_date(now, self.periods)
        self.assertEqual(due_date, datetime(2011, 2, 1, 17, 0, 0))

    def test_get_due_date_for_0_periods_end_duration_is_end_of_this_period(self):
        duration = self.durations[9]
        now = datetime(2011, 1, 3, 12, 0, 0)
        due_date = duration.get_due_date(now, self.periods)
        self.assertEqual(due_date, datetime(2011, 1, 3, 17, 0, 0))

    def test_get_due_date_for_0_periods_end_duration_outside_period_is_end_of_next_period(self):
        duration = self.durations[9]
        now = datetime(2011, 1, 1, 12, 0, 0) # Saturday
        due_date = duration.get_due_date(now, self.periods)
        self.assertEqual(due_date, datetime(2011, 1, 3, 17, 0, 0))

    def test_get_due_date_for_1_period_end_duration_is_end_of_next_period(self):
        duration = self.durations[10]
        now = datetime(2011, 1, 3, 12, 0, 0)
        due_date = duration.get_due_date(now, self.periods)
        self.assertEqual(due_date, datetime(2011, 1, 4, 17, 0, 0))

    def test_get_due_date_for_1_period_end_duration_outside_period_is_end_of_next_period(self):
        duration = self.durations[10]
        now = datetime(2011, 1, 1, 12, 0, 0) # Saturday
        due_date = duration.get_due_date(now, self.periods)
        self.assertEqual(due_date, datetime(2011, 1, 3, 17, 0, 0))


class TestPeriod(TestCase):
    def setUp(self):
        self.catalog = Catalog.objects.create(name="Test Catalog")
        self.period_weekdays_9_5 = Period.objects.create(
            catalog=self.catalog, name="Weekdays 9-5", days='0,1,2,3,4',
            start_time=time(9, 0, 0), end_time=time(17, 0, 0))
    
    def test_get_start_timestamps_generates_9am_every_weekday(self):
        now = datetime(2011, 1, 1, 12, 0, 0)
        start_times = self.period_weekdays_9_5.get_start_timestamps(now)
        next_10_start_times = start_times[:10]
        self.assertEqual(next_10_start_times, [datetime(2011, 1, 3, 9, 0, 0),
                                               datetime(2011, 1, 4, 9, 0, 0),
                                               datetime(2011, 1, 5, 9, 0, 0),
                                               datetime(2011, 1, 6, 9, 0, 0),
                                               datetime(2011, 1, 7, 9, 0, 0),
                                               datetime(2011, 1, 10, 9, 0, 0),
                                               datetime(2011, 1, 11, 9, 0, 0),
                                               datetime(2011, 1, 12, 9, 0, 0),
                                               datetime(2011, 1, 13, 9, 0, 0),
                                               datetime(2011, 1, 14, 9, 0, 0)])

    def test_get_start_timestamps_generates_5pm_every_weekday(self):
        now = datetime(2011, 1, 1, 12, 0, 0)
        end_times = self.period_weekdays_9_5.get_end_timestamps(now)
        next_10_end_times = end_times[:10]
        self.assertEqual(next_10_end_times, [datetime(2011, 1, 3, 17, 0, 0),
                                             datetime(2011, 1, 4, 17, 0, 0),
                                             datetime(2011, 1, 5, 17, 0, 0),
                                             datetime(2011, 1, 6, 17, 0, 0),
                                             datetime(2011, 1, 7, 17, 0, 0),
                                             datetime(2011, 1, 10, 17, 0, 0),
                                             datetime(2011, 1, 11, 17, 0, 0),
                                             datetime(2011, 1, 12, 17, 0, 0),
                                             datetime(2011, 1, 13, 17, 0, 0),
                                             datetime(2011, 1, 14, 17, 0, 0)])
