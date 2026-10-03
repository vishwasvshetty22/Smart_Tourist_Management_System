from django.contrib import admin
from .models import Hotel, HotelRoom, HotelBooking, HotelReview

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name','category','city','owner','star_rating','avg_rating','is_approved']
    list_filter = ['category','is_approved','location']
    list_editable = ['is_approved']
    search_fields = ['name','city']

@admin.register(HotelRoom)
class HotelRoomAdmin(admin.ModelAdmin):
    list_display = ['hotel','room_type','room_number','price_per_night','is_available']
    list_editable = ['is_available']

@admin.register(HotelBooking)
class HotelBookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id','tourist','hotel','room','status','total_amount']
    list_filter = ['status']

admin.site.register(HotelReview)
