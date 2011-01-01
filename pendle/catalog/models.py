import calendar

from django.db import models
from django.conf import settings
from django.utils.translation import ungettext as _n

from pendle.institution.models import Department, Course, Training
from pendle.utils.text import format_dollars
from pendle.utils.html import hyperlink


MARKDOWN_LINK = hyperlink('http://daringfireball.net/projects/markdown/'
                          'dingus', "Formatting help", target='_blank')

class ReservationDuration(models.Model):
    UNIT_CHOICES = (('period', "Period"),
                    ('hour', "Hour"),
                    ('day', "Day"))
    DUE_AT_CHOICES = (('exact', "Exact time"),
                      ('period_end', "End of period"))
    
    length = models.PositiveSmallIntegerField(default=1)
    unit = models.CharField(max_length=8, choices=UNIT_CHOICES,
                            default='day')
    due_at = models.CharField(max_length=20, choices=DUE_AT_CHOICES,
                              default='period_end')
    
    def __unicode__(self):
        return u"%d %s (at %s)" % (self.length,
                                   _n("%s", "%ss", self.length) % self.unit,
                                   self.get_due_at_display().lower())

class FinePolicy(models.Model):    
    per_day = models.DecimalField("amount per day", max_digits=6,
                                  decimal_places=2, default=0)
    per_period = models.DecimalField("amount per period", max_digits=6,
                                     decimal_places=2, default=0)
    per_hour = models.DecimalField("amount per hour", max_digits=6,
                                   decimal_places=2, default=0)
    flat_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    class Meta:
        verbose_name_plural = "fine policies"
    
    def __unicode__(self):
        fines = []
        if self.flat_fee > 0:
            fines.append(u"%s flat fee" % format_dollars(self.flat_fee))
        if self.per_day > 0:
            fines.append(u"%s per day" % format_dollars(self.per_day))
        if self.per_period > 0:
            fines.append(u"%s per period" % format_dollars(self.per_period))
        if self.per_hour > 0:
            fines.append(u"%s per hour" % format_dollars(self.per_hour))
        if fines:
            return u", ".join(fines)
        else:
            return u"No fee ($0)"
    

class Requirements(models.Model):
    CONNECTIVE_CHOICES = (('all', "All of these conditions"),
                          ('any', "Any of these conditions"))
    connective = models.CharField("must satisfy", max_length=4,
                                  choices=CONNECTIVE_CHOICES, default='all')
    departments = models.ManyToManyField(Department, blank=True)
    courses = models.ManyToManyField(Course, blank=True)
    training = models.ManyToManyField(Training, blank=True)

    class Meta:
        verbose_name_plural = "requirements"

    def __unicode__(self):
        requirements = []
        departments = self.departments.all()
        if departments:
            requirements.append("Departments: %s" %
                                ", ".join(map(unicode, departments)))
        courses = self.courses.all()
        if courses:
            requirements.append("Courses: %s" %
                                ", ".join(map(unicode, courses)))
        training = self.training.all()
        if training:
            requirements.append("Training: %s" %
                                ", ".join(map(unicode, training)))
        return u", ".join(requirements)


class CatalogManager(models.Manager):
    def get_or_default(self, pk=None, **kwargs):
        if pk is None:
            pk = kwargs.get('id', settings.DEFAULT_CATALOG)
        return self.get(pk=pk, **kwargs)

class Catalog(models.Model):
    name = models.CharField(max_length=75, unique=True)
    online = models.BooleanField(default=True,
        help_text="Uncheck to temporarily disallow reservations.")
    default_reservation_duration = models.ForeignKey(ReservationDuration,
        null=True, blank=True, related_name='catalogs',
        help_text="Determines when reservations are due, by default.<br/>Pol"
                  "icy categories or per-asset policies may override this.")
    default_fine_policy = models.ForeignKey(FinePolicy, null=True,
        blank=True, related_name='catalogs',
        help_text="Determines how late fees are calculated, by default.<br/>"
                  "Policy categories or per-asset policies may override "
                  "this.")
    default_requirements = models.ForeignKey(Requirements, null=True,
        blank=True, related_name='catalogs',
        help_text="Determines who is allowed to make reservations, by "
                  "default.<br/>Policy categories or per-asset policies may "
                  "override this.")
    receipt_prologue = models.TextField(blank=True, default="",
        help_text="Text to show at the top of receipts. " + MARKDOWN_LINK)
    receipt_epilogue = models.TextField(blank=True, default="",
        help_text="Text to show at the bottom of receipts. " + MARKDOWN_LINK)
    receipt_signature = models.BooleanField("signature on receipts",
        default=False, help_text="Show a signature line on receipts.")

    objects = CatalogManager()

    def __unicode__(self):
        return self.name

class Period(models.Model):
    catalog = models.ForeignKey(Catalog, related_name='periods')
    name = models.CharField("period name", max_length=75, null=True,
                            blank=True, help_text="For example: Period 1")
    days = models.CommaSeparatedIntegerField(max_length=13)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        ordering = ['catalog', 'name', 'start_time', 'days']

    def __unicode__(self):
        days = self.get_days()
        if len(days) == 7:
            day_string = u"Every day"
        else:
            ranges = []
            for day in days:
                if ranges and day == ranges[-1][-1] + 1:
                    ranges[-1].append(day)
                else:
                    ranges.append([day])
            day_strings = []
            for day_range in ranges:
                if len(day_range) > 1:
                    start, end = day_range[0], day_range[-1]
                    day_strings.append(u"%s-%s" % (calendar.day_abbr[start],
                                                   calendar.day_abbr[end]))
                else:
                    day = day_range[0]
                    day_strings.append(calendar.day_abbr[day])
            day_string = u", ".join(day_strings)
            time_string = u"%s - %s" % (self.start_time.strftime("%I:%M%p"),
                                        self.end_time.strftime("%I:%M%p"))
        return u"%s %s" % (day_string, time_string)

    def get_days(self):
        return sorted(set(int(d) for d in self.days.split(',')))

