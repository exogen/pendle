from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.utils.formats import number_format

from pendle.institution.models import (Profile, Department, Course,
                                       ScheduledCourse)
from pendle.institution.forms import ScheduledCourseForm
from pendle.fines.models import Fine, FinePayment
from pendle.utils import add
from pendle.utils.text import format_dollars
from pendle.utils.html import changelist_link
from pendle.utils.admin import related_list, count_link


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 1
    max_num = 1
    can_delete = False
    verbose_name_plural = "profile"

    fieldsets = [
        (None, {'fields': ('id_number', 'phone_number', 'address',
                           ('year', 'graduation_date'), 'staff_notes',
                           'picture', 'signed_agreement')})]

class FineInline(admin.TabularInline):
    model = Fine
    fk_name = 'customer'
    readonly_fields = ['date_issued']
    extra = 0

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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'staff_member':
            kwargs['initial'] = request.user
        return super(FinePaymentInline, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

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

    list_display += ['email',
                     related_list(User, 'departments',
                                  admin_order_field='departments__name'),
                     related_list(User, 'groups',
                                  admin_order_field='groups__name')]

    @add(list_display, "fines", allow_tags=True)
    def list_fines(self, user):
        amount_issued = sum(fine.amount for fine in user.fines.all())
        amount_paid = sum(payment.amount for payment in user.fine_payments.all())
        amount_due = amount_issued - amount_paid
        classes = ['fine']
        if amount_due > 0:
            classes.append('due')
        return '<p class="%s">%s<p>' % (' '.join(classes),
                                        format_dollars(amount_due))


class PendleGroupAdmin(GroupAdmin):
    list_display = ['__unicode__']

    @add(list_display, "users", allow_tags=True)
    def list_users(self, group):
        user_count = group.user_set.count()
        if user_count:
            link = changelist_link(User, "", {'groups__id__exact': group},
                                   title="Find users in this group")
            return '<p class="count">%s %s</p>' % (link,
                                                   number_format(user_count))
        else:
            return ""


class DepartmentAdmin(admin.ModelAdmin):
    filter_horizontal = ['users']
    list_display = ['__unicode__', 'subject_code',
                    count_link(Department, 'users')]


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
