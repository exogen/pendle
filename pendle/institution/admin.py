from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

from pendle.institution.models import (Profile, Department, Course,
                                       ScheduledCourse)
from pendle.utils import add
from pendle.utils.admin import count_link


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 1
    max_num = 1
    can_delete = False
    verbose_name_plural = "profile"


class PendleUserAdmin(UserAdmin):
    inlines = list(UserAdmin.inlines) + [ProfileInline]
    ordering = ['last_name', 'first_name', 'username']
    list_display = ['username', 'first_name', 'last_name']
    list_display_links = ['username']
    list_filter = ['groups', 'is_staff']
    list_per_page = 60
    search_fields = ['username', 'first_name', 'last_name', 'email',
                     'profile__id_number']

    for name, options in UserAdmin.fieldsets:
        if name in ("Permissions", "Important dates"):
            options['classes'] = ['collapse']

    @add(list_display, "ID number", admin_order_field='profile__id_number')
    def id_number(self, user):
        return user.get_profile().id_number or ""

    list_display += ['email']

    @add(list_display, "departments", admin_order_field='departments__name')
    def department(self, user):
        return u", ".join(map(unicode, user.departments.all()))

    @add(list_display, "groups", admin_order_field='groups__name')
    def group(self, user):
        return u", ".join(map(unicode, user.groups.all()))


class PendleGroupAdmin(GroupAdmin):
    pass


class DepartmentAdmin(admin.ModelAdmin):
    filter_horizontal = ['users']
    list_display = ['__unicode__', 'subject_code',
                    count_link(Department, 'users')]


class ScheduledCourseInline(admin.TabularInline):
    model = ScheduledCourse
    extra = 0
    filter_horizontal = ['students']


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
