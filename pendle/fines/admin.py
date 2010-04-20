from django.contrib import admin

from fines.models import Fine, FinePayment


class FineAdmin(admin.ModelAdmin):
    list_display = ['amount', 'customer', 'date_issued']
    list_filter = ['date_issued']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'staff_member':
            kwargs['initial'] = request.user
        return super(FineAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

class FinePaymentAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'staff_member':
            kwargs['initial'] = request.user
        return super(FinePaymentAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)


admin.site.register(Fine, FineAdmin)
admin.site.register(FinePayment, FinePaymentAdmin)
