from django.db import models
from accounts.models import User


class Notification(models.Model):
    TYPES = [
        ('booking_confirmed','Booking Confirmed'),('booking_cancelled','Booking Cancelled'),
        ('booking_rejected','Booking Rejected'),('payment_success','Payment Success'),
        ('new_booking','New Booking'),('listing_approved','Listing Approved'),
        ('listing_rejected','Listing Rejected'),('general','General'),
    ]
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type       = models.CharField(max_length=30, choices=TYPES, default='general')
    title      = models.CharField(max_length=200)
    message    = models.TextField()
    link       = models.CharField(max_length=300, blank=True)
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} – {self.title}"
