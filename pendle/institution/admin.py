from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.utils.formats import number_format

from pendle.institution.models import (Profile, Department, Course,
                                       ScheduledCourse)
from pendle.institution.forms import ScheduledCourseForm
from pendle.utils import add
from pendle.utils.html import changelist_link
from pendle.utils.admin import related_list, count_link


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

    list_display += ['email',
                     related_list(User, 'departments',
                                  admin_order_field='departments__name'),
                     related_list(User, 'groups',
                                  admin_order_field='groups__name')]


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
