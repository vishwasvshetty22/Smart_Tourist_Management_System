from django.contrib import admin
from .models import Vehicle, VehicleImage, VehicleBooking, VehicleReview

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['name','brand','model','vehicle_type','owner','location','price_per_day','is_approved','is_available']
    list_filter = ['vehicle_type','is_approved','is_available','location']
    search_fields = ['brand','model','registration_number']
    list_editable = ['is_approved','is_available']

@admin.register(VehicleBooking)
class VehicleBookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id','tourist','vehicle','status','total_amount','created_at']
    list_filter = ['status']
    search_fields = ['booking_id']

admin.site.register(VehicleImage)
admin.site.register(VehicleReview)
