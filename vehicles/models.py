from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User, TouristLocation


class Vehicle(models.Model):
    TYPE_CHOICES = [('bike','Bike'),('scooter','Scooter'),('car','Car'),
                    ('suv','SUV'),('bus','Mini Bus'),('cycle','Cycle')]
    FUEL_CHOICES = [('petrol','Petrol'),('diesel','Diesel'),
                    ('electric','Electric'),('hybrid','Hybrid')]
    TRANS_CHOICES = [('manual','Manual'),('automatic','Automatic')]

    owner               = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    name                = models.CharField(max_length=200)
    vehicle_type        = models.CharField(max_length=20, choices=TYPE_CHOICES)
    brand               = models.CharField(max_length=100)
    model               = models.CharField(max_length=100)
    year                = models.PositiveIntegerField()
    registration_number = models.CharField(max_length=50, unique=True)
    fuel_type           = models.CharField(max_length=20, choices=FUEL_CHOICES, default='petrol')
    transmission        = models.CharField(max_length=20, choices=TRANS_CHOICES, default='manual')
    seating_capacity    = models.PositiveIntegerField(default=2)
    description         = models.TextField()
    features            = models.TextField(blank=True)
    price_per_hour      = models.DecimalField(max_digits=8, decimal_places=2)
    price_per_day       = models.DecimalField(max_digits=8, decimal_places=2)
    security_deposit    = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    location            = models.ForeignKey(TouristLocation, on_delete=models.SET_NULL, null=True, related_name='vehicles')
    pickup_address      = models.TextField()
    is_available        = models.BooleanField(default=True)
    is_approved         = models.BooleanField(default=False)
    is_featured         = models.BooleanField(default=False)
    total_bookings      = models.PositiveIntegerField(default=0)
    avg_rating          = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    thumbnail           = models.ImageField(upload_to='vehicles/thumbnails/', null=True, blank=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vehicles'
        ordering = ['-avg_rating', '-created_at']

    def __str__(self):
        return f"{self.brand} {self.model} ({self.vehicle_type})"

    def get_features_list(self):
        return [f.strip() for f in self.features.split(',') if f.strip()]


class VehicleImage(models.Model):
    vehicle    = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='images')
    image      = models.ImageField(upload_to='vehicles/images/')
    caption    = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order      = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'vehicle_images'
        ordering = ['order']


class VehicleBooking(models.Model):
    STATUS = [('pending','Pending'),('confirmed','Confirmed'),
              ('active','Active'),('completed','Completed'),
              ('cancelled','Cancelled'),('rejected','Rejected')]
    RENTAL = [('hourly','Hourly'),('daily','Daily')]

    tourist          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicle_bookings')
    vehicle          = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='bookings')
    booking_id       = models.CharField(max_length=20, unique=True)
    rental_type      = models.CharField(max_length=10, choices=RENTAL, default='daily')
    start_datetime   = models.DateTimeField()
    end_datetime     = models.DateTimeField()
    pickup_location  = models.TextField()
    special_requests = models.TextField(blank=True)
    base_amount      = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount     = models.DecimalField(max_digits=10, decimal_places=2)
    status           = models.CharField(max_length=20, choices=STATUS, default='pending')
    cancel_reason    = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vehicle_bookings'
        ordering = ['-created_at']

    def __str__(self):
        return self.booking_id


class VehicleReview(models.Model):
    vehicle     = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='reviews')
    tourist     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicle_reviews')
    booking     = models.OneToOneField(VehicleBooking, on_delete=models.SET_NULL, null=True, related_name='review')
    rating      = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vehicle_reviews'
