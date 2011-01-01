from datetime import datetime

from django.test import TestCase
from django.db.models.query import QuerySet

from pendle.assets.models import Asset


class TestAssetManagerCheckedOut(TestCase):
    fixtures = ['test_users', 'test_catalog', 'test_assets',
                'test_reservations']

    def test_checked_out_if_reservation_has_no_in_transaction(self):
        assets = Asset.objects.checked_out()
        self.assertTrue(isinstance(assets, QuerySet))
        self.assertEqual(list(assets), list(Asset.objects.filter(pk=1)))

class TestAssetManagerCheckedIn(TestCase):
    fixtures = ['test_users', 'test_catalog', 'test_assets',
                'test_reservations']
    
    def test_checked_in_if_returned_or_never_checked_out(self):
        assets = Asset.objects.checked_in()
        self.assertTrue(isinstance(assets, QuerySet))
        self.assertEqual(list(assets),
                         list(Asset.objects.filter(pk__in=[2, 3])))

class TestAssetManagerOverdue(TestCase):
    fixtures = ['test_users', 'test_catalog', 'test_assets',
                'test_reservations']

    def test_not_overdue_if_now_is_before_due_date(self):
        now = datetime(2010, 10, 30, 16, 43, 59)
        assets = Asset.objects.overdue(now)
        self.assertTrue(isinstance(assets, QuerySet))
        self.assertEqual(list(assets), [])

    def test_not_overdue_if_now_is_due_date(self):
        now = datetime(2010, 10, 30, 16, 44, 00)
        assets = Asset.objects.overdue(now)
        self.assertTrue(isinstance(assets, QuerySet))
        self.assertEqual(list(assets), [])

    def test_overdue_if_now_is_after_due_date(self):
        now = datetime(2010, 10, 30, 16, 44, 01)
        assets = Asset.objects.overdue(now)
        self.assertTrue(isinstance(assets, QuerySet))
        self.assertEqual(list(assets), list(Asset.objects.filter(pk=1)))

class TestAssetManagerAvailable(TestCase):
    fixtures = ['test_users', 'test_catalog', 'test_assets',
                'test_reservations']
    
    def test_available_if_checked_in(self):
        assets = Asset.objects.available()
        self.assertEqual(list(assets),
                         list(Asset.objects.filter(pk__in=[2, 3])))

