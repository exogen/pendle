from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.formats import date_format

from pendle.catalog.models import Catalog
from pendle.utils.text import truncate


class Note(models.Model):
    author = models.ForeignKey(User, related_name='notes',
        limit_choices_to={'is_staff': True})
    message = models.TextField()
    timestamp = models.DateTimeField(default=datetime.now)
    catalog = models.ForeignKey(Catalog, null=True, blank=True,
        related_name='notes')

    class Meta:
        ordering = ['-timestamp']

    def __unicode__(self):
        name = self.author.get_full_name() or self.author.username
        return u"%s on %s: %s" % (name, date_format(self.timestamp),
                                  truncate(self.message, 30))

