import itertools
from datetime import datetime
from operator import itemgetter

import dateutil
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR
from dateutil.rrule import rrule, DAILY
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext

from pendle.catalog.models import Catalog
from pendle.reservations.models import Transaction, Reservation
from pendle.fines.models import Fine, FinePayment


TWO_WEEKS_LAST_MONDAY = relativedelta(weeks=2, weekday=MO(-1))
FOUR_WEEKS_NEXT_FRIDAY = relativedelta(weeks=4, weekday=FR)
CALENDAR_DAYS = [MO, TU, WE, TH, FR]

def home(request):
    return redirect('admin:index')

def get_calendar_data(catalog, now=None):
    if now is None:
        now = datetime.now()
    today = now.date()
    calendar_start = today - TWO_WEEKS_LAST_MONDAY
    calendar_end = today + FOUR_WEEKS_NEXT_FRIDAY
    calendar_days = rrule(DAILY, dtstart=calendar_start, until=calendar_end,
                          byweekday=CALENDAR_DAYS)
    calendar_data = []
    week = []
    for day in calendar_days:
        data = {'datetime': day, 'date': day.date()}
        data['is_today'] = data['date'] == today
        data['is_previous_month'] = day.month != now.month and day < now
        data['is_next_month'] = day.month != now.month and day > now
        out_query = {'transaction_out__catalog': catalog.id,
                     'transaction_out__timestamp__year': day.year,
                     'transaction_out__timestamp__month': day.month,
                     'transaction_out__timestamp__day': day.day}
        in_query = {'transaction_in__catalog': catalog.id,
                    'transaction_in__timestamp__year': day.year,
                    'transaction_in__timestamp__month': day.month,
                    'transaction_in__timestamp__day': day.day}
        due_query = {'transaction_out__catalog': catalog.id,
                     'transaction_in__isnull': 1,
                     'due_date__year': day.year,
                     'due_date__month': day.month,
                     'due_date__day': day.day,
                     'due_date__gt': now}
        overdue_query = {'transaction_out__catalog': catalog.id,
                         'transaction_in__isnull': 1,
                         'due_date__year': day.year,
                         'due_date__month': day.month,
                         'due_date__day': day.day,
                         'due_date__lte': now}
        data['reservations_out'] = Reservation.objects.filter(**out_query)
        data['reservations_in'] = Reservation.objects.filter(**in_query)
        data['reservations_due'] = Reservation.objects.filter(**due_query)
        data['reservations_overdue'] = Reservation.objects.filter(**overdue_query)
        data['queries'] = {'out': out_query, 'in': in_query, 'due': due_query,
                           'overdue': overdue_query}
        week.append(data)
        if len(week) == 5:
            calendar_data.append(week)
            week = []
    return calendar_data

def get_activity_stream(catalog, now=None, max_num=25):
    if now is None:
        now = datetime.now()
    stream_start = now.date() - TWO_WEEKS_LAST_MONDAY
    events = []
    transactions = Transaction.objects.filter(
        timestamp__gte=stream_start,
        catalog=catalog)
    for transaction in transactions[:max_num]:
        events.append({'type': 'transaction',
                       'transaction': transaction,
                       'reservations_out': transaction.reservations_out.all(),
                       'reservations_in': transaction.reservations_in.all(),
                       'timestamp': transaction.timestamp})

    fine_payments = FinePayment.objects.filter(
        date_received__gte=stream_start).order_by('-date_received')
    for fine_payment in fine_payments[:max_num]:
        events.append({'type': 'fine-payment',
                       'fine_payment': fine_payment,
                       'timestamp': fine_payment.date_received})
    
    overdue = Reservation.objects.filter(
        transaction_in__isnull=True,
        transaction_out__catalog=catalog,
        due_date__gte=stream_start,
        due_date__lte=now).order_by('-due_date')
    for reservation in overdue[:max_num]:
        events.append({'type': 'overdue',
                       'reservation': reservation,
                       'timestamp': reservation.due_date})

    return sorted(events, key=itemgetter('timestamp'), reverse=True)

def dashboard(request):
    catalog = Catalog.objects.get_or_default()
    now = datetime.now()
    today = now.date()
    calendar_data = get_calendar_data(catalog, now)
    activity_stream = get_activity_stream(catalog, now)
    return render_to_response("pendle/dashboard.html", {
        'title': "Dashboard", 'catalog': catalog, 'today': today, 'now': now,
        'calendar_data': calendar_data, 'activity_stream': activity_stream},
        context_instance=RequestContext(request))

