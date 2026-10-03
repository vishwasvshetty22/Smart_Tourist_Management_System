from django.contrib import admin
from .models import TourGuide, GuideBooking, GuideReview

@admin.register(TourGuide)
class TourGuideAdmin(admin.ModelAdmin):
    list_display = ['name','expertise','years_experience','avg_rating','is_approved','is_available']
    list_filter = ['expertise','is_approved']
    list_editable = ['is_approved']

@admin.register(GuideBooking)
class GuideBookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id','tourist','guide','status','total_amount','created_at']
    list_filter = ['status']

admin.site.register(GuideReview)
