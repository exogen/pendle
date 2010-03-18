from django.contrib import admin

from pendle.extras.models import Note
from pendle.utils.admin import field_value, related_link


class NoteAdmin(admin.ModelAdmin):
    list_display = [field_value(Note, 'message', max_length=60),
                    related_link(Note, 'author'),
                    'timestamp', field_value(Note, 'catalog', "All catalogs")]
    list_filter = ['timestamp', 'catalog']
    search_fields = ['message', 'author__username', 'author__first_name',
                     'author__last_name']
    readonly_fields = ['timestamp']


admin.site.register(Note, NoteAdmin)
