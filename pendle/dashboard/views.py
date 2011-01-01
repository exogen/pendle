import itertools
from datetime import datetime
from operator import itemgetter

import dateutil
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR
from dateutil.rrule import rrule, DAILY
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Sum
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required

from pendle.catalog.models import Catalog
from pendle.reservations.models import Transaction, Reservation
from pendle.fines.models import Fine, FinePayment
from pendle.dashboard.forms import CustomizeActivityFeedForm
from pendle.utils.views import JsonResponse


TWO_WEEKS_LAST_MONDAY = relativedelta(weeks=2, weekday=MO(-1))
TWO_WEEKS_NEXT_FRIDAY = relativedelta(weeks=2, weekday=FR)
CALENDAR_DAYS = [MO, TU, WE, TH, FR]

def get_calendar_data(catalog, now=None):
    if now is None:
        now = datetime.now()
    today = now.date()
    calendar_start = today - TWO_WEEKS_LAST_MONDAY
    calendar_end = today + TWO_WEEKS_NEXT_FRIDAY
    calendar_days = rrule(DAILY, dtstart=calendar_start, until=calendar_end,
                          byweekday=CALENDAR_DAYS)
    calendar_data = []
    week = []
    for day in calendar_days:
        data = {'datetime': day, 'date': day.date()}
        data['is_today'] = data['date'] == today
        data['is_previous_month'] = day.month != now.month and day < now
        data['is_next_month'] = day.month != now.month and day > now
        out_query = {'transaction_out__catalog': catalog.pk,
                     'transaction_out__timestamp__year': day.year,
                     'transaction_out__timestamp__month': day.month,
                     'transaction_out__timestamp__day': day.day}
        in_query = {'transaction_in__catalog': catalog.pk,
                    'transaction_in__timestamp__year': day.year,
                    'transaction_in__timestamp__month': day.month,
                    'transaction_in__timestamp__day': day.day}
        due_query = {'transaction_out__catalog': catalog.pk,
                     'transaction_in__isnull': 1,
                     'due_date__year': day.year,
                     'due_date__month': day.month,
                     'due_date__day': day.day,
                     'due_date__gt': now}
        overdue_query = {'transaction_out__catalog': catalog.pk,
                         'transaction_in__isnull': 1,
                         'due_date__year': day.year,
                         'due_date__month': day.month,
                         'due_date__day': day.day,
                         'due_date__lte': now}
        data['reservations'] = {
            'out': Reservation.objects.filter(**out_query),
            'in': Reservation.objects.filter(**in_query),
            'due': Reservation.objects.filter(**due_query),
            'overdue': Reservation.objects.filter(**overdue_query)}
        data['queries'] = {'out': out_query, 'in': in_query, 'due': due_query,
                           'overdue': overdue_query}
        week.append(data)
        if len(week) == 5:
            calendar_data.append(week)
            week = []
    return calendar_data

def get_activity_stream(catalog, now=None, limit=25, types=None):
    if now is None:
        now = datetime.now()
    stream_start = now.date() - TWO_WEEKS_LAST_MONDAY
    events = []

    if types is None or 'transaction' in types:
        transactions = Transaction.objects.filter(
            timestamp__gte=stream_start,
            catalog=catalog)
        for transaction in transactions[:limit]:
            events.append({
                'type': 'transaction',
                'transaction': transaction,
                'reservations_out': transaction.reservations_out.all(),
                'reservations_in': transaction.reservations_in.all(),
                'timestamp': transaction.timestamp})

    if types is None or 'fine-paid' in types:
        fine_payments = FinePayment.objects.filter(
            date_received__gte=stream_start).order_by('-date_received')
        for fine_payment in fine_payments[:limit]:
            events.append({'type': 'fine-paid',
                           'fine_payment': fine_payment,
                           'timestamp': fine_payment.date_received})
    
    if types is None or 'overdue' in types:
        overdue = Reservation.objects.filter(
            transaction_in__isnull=True,
            transaction_out__catalog=catalog,
            due_date__gte=stream_start,
            due_date__lte=now).order_by('-due_date')
        for reservation in overdue[:limit]:
            events.append({'type': 'overdue',
                           'reservation': reservation,
                           'timestamp': reservation.due_date})

    return sorted(events, key=itemgetter('timestamp'), reverse=True)[:limit]

def get_fines_due():
    fines = Fine.objects.values('customer').annotate(
        total=Sum('amount')).order_by()
    payments = FinePayment.objects.values('customer').annotate(
        total=Sum('amount')).order_by()
    customer_payments = {}
    for payment in payments:
        customer_payments[payment['customer']] = payment['total']
    fines_due = []
    for fine in fines:
        customer_id = fine['customer']
        amount = fine['total']
        if customer_id in customer_payments:
            amount -= customer_payments[customer_id]
        fines_due.append({'customer': User.objects.get(pk=customer_id),
                          'amount': amount})
    return sorted(fines_due, key=itemgetter('amount'), reverse=True)

@staff_member_required
def dashboard(request):
    catalog = Catalog.objects.get_or_default()
    now = datetime.now()
    today = now.date()
    calendar_data = get_calendar_data(catalog, now)
    activity_options = request.session.get('dashboard.activity.options', {})
    activity_stream = get_activity_stream(catalog, now, **activity_options)
    fines_due = get_fines_due()
    assets = catalog.assets.all()
    reservations_out = Reservation.objects.filter(
        asset__catalog=catalog,
        transaction_in__isnull=True)
    reservations_overdue = Reservation.objects.filter(
        asset__catalog=catalog,
        transaction_in__isnull=True,
        due_date__lte=now)
    return render_to_response("dashboard/dashboard.html", {
        'title': "Dashboard",
        'catalog': catalog,
        'today': today,
        'now': now,
        'calendar_data': calendar_data,
        'activity_stream': activity_stream,
        'fines_due': fines_due,
        'assets': assets,
        'reservations_out': reservations_out,
        'reservations_overdue': reservations_overdue,
        }, context_instance=RequestContext(request))

@staff_member_required
def activity_options(request):
    if request.method == 'POST':
        form = CustomizeActivityFeedForm(request.POST, auto_id='activity-%s')
        if form.is_valid():
            request.session['dashboard.activity.options'] = form.cleaned_data
    else:
        form = CustomizeActivityFeedForm(auto_id='activity-%s',
            initial=request.session.get('dashboard.activity.options', {}))
    return render_to_response("dashboard/includes/customize_activity.html",
        {'form': form}, context_instance=RequestContext(request))

