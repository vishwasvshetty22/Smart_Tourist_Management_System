from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User, TouristLocation


class TourGuide(models.Model):
    EXPERTISE = [('historical','Historical'),('adventure','Adventure'),('nature','Nature'),
                 ('cultural','Cultural'),('food','Food & Culinary'),('photography','Photography'),('general','General')]

    user             = models.OneToOneField(User, on_delete=models.CASCADE, related_name='guide_profile')
    years_experience = models.PositiveIntegerField(default=1)
    expertise        = models.CharField(max_length=30, choices=EXPERTISE, default='general')
    bio              = models.TextField()
    languages        = models.CharField(max_length=300)
    locations        = models.ManyToManyField(TouristLocation, related_name='guides', blank=True)
    price_per_hour   = models.DecimalField(max_digits=8, decimal_places=2)
    price_per_day    = models.DecimalField(max_digits=8, decimal_places=2)
    is_available     = models.BooleanField(default=True)
    profile_image    = models.ImageField(upload_to='guides/', null=True, blank=True)
    avg_rating       = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_tours      = models.PositiveIntegerField(default=0)
    is_approved      = models.BooleanField(default=False)
    is_featured      = models.BooleanField(default=False)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tourist_guides'
        ordering = ['-avg_rating']

    def __str__(self):
        return self.user.get_full_name()

    @property
    def name(self):
        return self.user.get_full_name()

    def get_languages_list(self):
        return [l.strip() for l in self.languages.split(',') if l.strip()]


class GuideBooking(models.Model):
    STATUS = [('pending','Pending'),('confirmed','Confirmed'),
              ('completed','Completed'),('cancelled','Cancelled'),('rejected','Rejected')]
    TYPES  = [('hourly','Hourly'),('daily','Full Day'),('multi_day','Multi-Day')]

    tourist          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guide_bookings')
    guide            = models.ForeignKey(TourGuide, on_delete=models.CASCADE, related_name='bookings')
    booking_id       = models.CharField(max_length=20, unique=True)
    location         = models.ForeignKey(TouristLocation, on_delete=models.SET_NULL, null=True, blank=True)
    booking_type     = models.CharField(max_length=20, choices=TYPES, default='daily')
    start_datetime   = models.DateTimeField()
    end_datetime     = models.DateTimeField()
    meeting_point    = models.TextField()
    group_size       = models.PositiveIntegerField(default=1)
    special_requests = models.TextField(blank=True)
    total_amount     = models.DecimalField(max_digits=10, decimal_places=2)
    status           = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'guide_bookings'
        ordering = ['-created_at']

    def __str__(self):
        return self.booking_id


class GuideReview(models.Model):
    guide       = models.ForeignKey(TourGuide, on_delete=models.CASCADE, related_name='reviews')
    tourist     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guide_reviews')
    rating      = models.PositiveIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    review_text = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'guide_reviews'
