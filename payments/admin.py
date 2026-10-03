from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id','user','booking_type','booking_id','amount','status','initiated_at']
    list_filter = ['status','booking_type','payment_method']
    search_fields = ['transaction_id','booking_id']
