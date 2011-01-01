from datetime import datetime

from django.test import TestCase
from django.db.models.query import QuerySet

from pendle.reservations.models import Reservation, Transaction
from pendle.assets.models import Asset


class TestReservationManagerCheckedOut(TestCase):
    fixtures = ['test_users', 'test_catalog', 'test_assets',
                'test_reservations']

    def test_checked_out_if_reservation_has_no_in_transaction(self):
        query = Reservation.objects.checked_out()
        self.assertTrue(isinstance(query, QuerySet))
        self.assertEqual(list(query), list(Reservation.objects.filter(pk=2)))

class TestReservationManagerCheckedIn(TestCase):
    fixtures = ['test_users', 'test_catalog', 'test_assets',
                'test_reservations']

    def test_checked_in_if_reservation_has_in_transaction(self):
        query = Reservation.objects.checked_in()
        self.assertTrue(isinstance(query, QuerySet))
        self.assertEqual(list(query),
                         list(Reservation.objects.filter(pk__in=[1, 3, 4])))

class TestReservationManagerOverdue(TestCase):
    fixtures = ['test_users', 'test_catalog', 'test_assets',
                'test_reservations']

    def test_not_overdue_if_now_is_before_due_date(self):
        now = datetime(2010, 10, 30, 16, 43, 59)
        query = Reservation.objects.overdue(now)
        self.assertTrue(isinstance(query, QuerySet))
        self.assertEqual(list(query), [])

    def test_not_overdue_if_now_is_due_date(self):
        now = datetime(2010, 10, 30, 16, 44, 00)
        query = Reservation.objects.overdue(now)
        self.assertTrue(isinstance(query, QuerySet))
        self.assertEqual(list(query), [])

    def test_overdue_if_now_is_after_due_date(self):
        now = datetime(2010, 10, 30, 16, 44, 01)
        query = Reservation.objects.overdue(now)
        self.assertTrue(isinstance(query, QuerySet))
        self.assertEqual(list(query), list(Reservation.objects.filter(pk=2)))

class TestTransactionAssets(TestCase):
    fixtures = ['test_users', 'test_catalog', 'test_assets',
                'test_reservations']

    def test_assets_has_checked_in_and_checked_out_assets(self):
        t1, t2, t3 = Transaction.objects.order_by('pk')
        self.assertTrue(isinstance(t1.assets, QuerySet))
        self.assertEqual(list(t1.assets),
                         list(Asset.objects.filter(pk__in=[1, 3])))
        self.assertEqual(list(t2.assets),
                         list(Asset.objects.filter(pk__in=[1, 2, 3])))
        self.assertEqual(list(t3.assets),
                         list(Asset.objects.filter(pk__in=[2])))

    def test_assets_out_has_checked_out_assets(self):
        t1, t2, t3 = Transaction.objects.order_by('pk')
        self.assertTrue(isinstance(t1.assets_out, QuerySet))
        self.assertEqual(list(t1.assets_out),
                         list(Asset.objects.filter(pk__in=[1, 3])))
        self.assertEqual(list(t2.assets_out),
                         list(Asset.objects.filter(pk__in=[1])))
        self.assertEqual(list(t3.assets_out),
                         list(Asset.objects.filter(pk__in=[2])))

    def test_assets_in_has_checked_in_assets(self):
        t1, t2, t3 = Transaction.objects.order_by('pk')
        self.assertTrue(isinstance(t1.assets_in, QuerySet))
        self.assertEqual(list(t1.assets_in),
                         list(Asset.objects.filter(pk__in=[])))
        self.assertEqual(list(t2.assets_in),
                         list(Asset.objects.filter(pk__in=[1, 2, 3])))
        self.assertEqual(list(t3.assets_in),
                         list(Asset.objects.filter(pk__in=[])))

