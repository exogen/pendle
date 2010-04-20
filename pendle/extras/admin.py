from django import forms
from django.contrib import admin
from django.contrib.auth.models import User

from pendle.extras.models import Note
from pendle.catalog.models import Catalog
from pendle.utils.admin import field_value, related_link


class NoteAdmin(admin.ModelAdmin):
    list_display = [field_value(Note, 'message', max_length=60),
                    related_link(Note, 'author'),
                    'timestamp', field_value(Note, 'catalog', "All catalogs")]
    list_filter = ['timestamp', 'catalog']
    search_fields = ['message', 'author__username', 'author__first_name',
                     'author__last_name']
    readonly_fields = ['timestamp']
    fieldsets = [(None, {'fields': ('message', 'catalog', 'author',
                                    'timestamp')})]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'author':
            kwargs['initial'] = request.user
        return super(NoteAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)


admin.site.register(Note, NoteAdmin)
