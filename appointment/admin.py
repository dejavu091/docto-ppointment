from django.contrib import admin
from .models import Product, PricingPlan, ContactInquiry, Appointment, Hospital, Service, Doctor


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'created_at')
    search_fields = ('name', 'description')


@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class DoctorInline(admin.TabularInline):
    model = Doctor
    extra = 1


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'is_active', 'created_at')
    search_fields = ('name', 'address', 'phone')
    list_filter = ('is_active',)
    filter_horizontal = ('services',)
    inlines = [DoctorInline]


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'hospital', 'phone', 'is_available', 'created_at')
    search_fields = ('name', 'specialty', 'hospital__name')
    list_filter = ('is_available', 'hospital')


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject')
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"Marked {updated} inquiry(s) as read.")
    mark_as_read.short_description = 'Mark selected inquiries as read'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'department', 'service', 'hospital', 'doctor', 'is_read', 'date', 'time', 'created_at')
    list_filter = ('is_read', 'date')
    search_fields = ('name', 'email', 'phone', 'department')
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"Marked {updated} appointment(s) as read.")
    mark_as_read.short_description = 'Mark selected appointments as read'
