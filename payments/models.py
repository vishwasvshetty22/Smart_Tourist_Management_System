from django.db import models
from accounts.models import User


class Payment(models.Model):
    STATUS  = [('pending','Pending'),('success','Success'),('failed','Failed'),('refunded','Refunded')]
    METHODS = [('card','Card'),('upi','UPI'),('netbanking','Net Banking'),('simulation','Simulated')]
    BTYPES  = [('vehicle','Vehicle'),('hotel','Hotel'),('guide','Guide')]

    user           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    transaction_id = models.CharField(max_length=100, unique=True)
    booking_type   = models.CharField(max_length=20, choices=BTYPES)
    booking_id     = models.CharField(max_length=20)
    amount         = models.DecimalField(max_digits=10, decimal_places=2)
    currency       = models.CharField(max_length=10, default='INR')
    payment_method = models.CharField(max_length=20, choices=METHODS, default='simulation')
    status         = models.CharField(max_length=20, choices=STATUS, default='pending')
    initiated_at   = models.DateTimeField(auto_now_add=True)
    completed_at   = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-initiated_at']

    def __str__(self):
        return f"{self.transaction_id} — ₹{self.amount} ({self.status})"
