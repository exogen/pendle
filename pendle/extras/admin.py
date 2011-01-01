from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from adminbrowse import link_to_change, truncated_field

from pendle.extras.models import Note
from pendle.catalog.models import Catalog
from pendle.utils.admin import PendleModelAdmin


class NoteAdmin(PendleModelAdmin):
    list_display = [truncated_field(Note, 'message', 80),
                    link_to_change(Note, 'author'), 'timestamp',
                    link_to_change(Note, 'catalog')]
    list_filter = ['timestamp', 'catalog']
    search_fields = ['message', 'author__username', 'author__first_name',
                     'author__last_name']
    readonly_fields = ['timestamp']
    select_related_fields = ['author', 'catalog']
    fieldsets = [(None, {'fields': ('message', 'catalog', 'author',
                                    'timestamp')})]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'author':
            kwargs['initial'] = request.user
        return super(NoteAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

    class Media:
        css = {'all': ('adminbrowse/css/adminbrowse.css',)}

admin.site.register(Note, NoteAdmin)
