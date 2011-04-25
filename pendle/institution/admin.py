from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.utils.formats import number_format
from django.db import models
from adminbrowse import (ChangeListTemplateColumn, link_to_changelist,
                         related_list)

from pendle.institution.models import (Profile, Department, Course,
                                       ScheduledCourse)
from pendle.institution.forms import ScheduledCourseForm
from pendle.fines.models import Fine, FinePayment
from pendle.fines.widgets import DollarsInput
from pendle.utils import add
from pendle.utils.admin import PendleModelAdmin


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 1
    max_num = 1
    can_delete = False
    verbose_name_plural = "profile"

    fieldsets = [
        (None, {'fields': ('id_number', 'phone_number', 'address',
                           ('year', 'graduation_date'), 'staff_notes',
                           'signed_agreement')})]

class FineInline(admin.TabularInline):
    model = Fine
    fk_name = 'customer'
    readonly_fields = ['date_issued']
    extra = 0
    formfield_overrides = {
        models.DecimalField: {'widget': DollarsInput, 'localize': True}}


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'staff_member':
            kwargs['initial'] = request.user
        return super(FineInline, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

class FinePaymentInline(admin.TabularInline):
    model = FinePayment
    fk_name = 'customer'
    readonly_fields = ['date_received']
    extra = 0
    formfield_overrides = {
        models.DecimalField: {'widget': DollarsInput, 'localize': True}}

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'staff_member':
            kwargs['initial'] = request.user
        return super(FinePaymentInline, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

class FinesDueColumn(ChangeListTemplateColumn):
    template_name = "fines/includes/amount_due.html"

    def get_context(self, user):
        context = super(FinesDueColumn, self).get_context(user)
        context['amount_due'] = Fine.objects.get_amount_due(user)
        return context

fines_column = FinesDueColumn

class PendleUserAdmin(UserAdmin):
    inlines = [ProfileInline, FineInline, FinePaymentInline]
    ordering = ['last_name', 'first_name', 'username']
    list_display = ['username', 'first_name', 'last_name']
    list_display_links = ['username']
    list_filter = ['groups', 'is_staff', 'date_joined']
    list_per_page = 60
    search_fields = ['username', 'first_name', 'last_name', 'email',
                     'profile__id_number']

    for name, options in UserAdmin.fieldsets:
        if name in ("Permissions", "Important dates"):
            options['classes'] = ['collapse']

    @add(list_display, "ID number", admin_order_field='profile__id_number')
    def id_number(self, user):
        return user.get_profile().id_number or ""

    list_display += ['email', related_list(User, 'departments'),
                     related_list(User, 'groups'), fines_column("fines")]

    def lookup_allowed(self, *args, **kwargs):
        return True

    class Media:
        css = {'all': ('adminbrowse/css/adminbrowse.css',)}

class PendleGroupAdmin(PendleModelAdmin, GroupAdmin):
    list_display = ['__unicode__', link_to_changelist(Group, 'user_set')]

    def lookup_allowed(self, *args, **kwargs):
        return True

class DepartmentAdmin(PendleModelAdmin):
    filter_horizontal = ['users']
    list_display = ['__unicode__', 'subject_code',
                    link_to_changelist(Department, 'users')]

class ScheduledCourseInline(admin.TabularInline):
    model = ScheduledCourse
    form = ScheduledCourseForm
    extra = 0

class CourseAdmin(admin.ModelAdmin):
    inlines = [ScheduledCourseInline]
    list_display = ['__unicode__', 'title']
    list_display_links = list_display
    list_filter = ['subject_code']
    search_fields = ['subject_code', 'number', 'title']

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, PendleUserAdmin)
admin.site.register(Group, PendleGroupAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Course, CourseAdmin)
