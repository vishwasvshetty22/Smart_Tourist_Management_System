from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User, TouristLocation


class Hotel(models.Model):
    CAT = [('budget','Budget'),('standard','Standard'),('deluxe','Deluxe'),
           ('luxury','Luxury'),('resort','Resort'),('boutique','Boutique'),('heritage','Heritage')]

    owner        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotels')
    name         = models.CharField(max_length=200)
    slug         = models.SlugField(unique=True)
    category     = models.CharField(max_length=20, choices=CAT, default='standard')
    description  = models.TextField()
    star_rating  = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1),MaxValueValidator(5)])
    location     = models.ForeignKey(TouristLocation, on_delete=models.SET_NULL, null=True, related_name='hotels')
    address      = models.TextField()
    city         = models.CharField(max_length=100)
    state        = models.CharField(max_length=100)
    amenities    = models.TextField(blank=True)
    phone        = models.CharField(max_length=20)
    email        = models.EmailField(blank=True)
    thumbnail    = models.ImageField(upload_to='hotels/thumbnails/', null=True, blank=True)
    is_approved  = models.BooleanField(default=False)
    is_featured  = models.BooleanField(default=False)
    avg_rating   = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_bookings = models.PositiveIntegerField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hotels'
        ordering = ['-avg_rating']

    def __str__(self):
        return self.name

    def get_amenities_list(self):
        return [a.strip() for a in self.amenities.split(',') if a.strip()]

    @property
    def min_price(self):
        r = self.rooms.filter(is_available=True).order_by('price_per_night').first()
        return r.price_per_night if r else 0


class HotelRoom(models.Model):
    TYPES = [('single','Single'),('double','Double'),('twin','Twin'),
             ('suite','Suite'),('deluxe','Deluxe'),('family','Family')]

    hotel           = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_type       = models.CharField(max_length=20, choices=TYPES)
    room_number     = models.CharField(max_length=20)
    capacity        = models.PositiveIntegerField(default=2)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    amenities       = models.TextField(blank=True)
    has_ac          = models.BooleanField(default=True)
    has_wifi        = models.BooleanField(default=True)
    thumbnail       = models.ImageField(upload_to='hotels/rooms/', null=True, blank=True)
    is_available    = models.BooleanField(default=True)

    class Meta:
        db_table = 'hotel_rooms'

    def __str__(self):
        return f"{self.hotel.name} - Room {self.room_number}"


class HotelBooking(models.Model):
    STATUS = [('pending','Pending'),('confirmed','Confirmed'),
              ('checked_in','Checked In'),('checked_out','Checked Out'),
              ('cancelled','Cancelled')]

    tourist          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotel_bookings')
    hotel            = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings')
    room             = models.ForeignKey(HotelRoom, on_delete=models.CASCADE, related_name='bookings')
    booking_id       = models.CharField(max_length=20, unique=True)
    guests_count     = models.PositiveIntegerField(default=1)
    guest_name       = models.CharField(max_length=200)
    guest_phone      = models.CharField(max_length=20)
    special_requests = models.TextField(blank=True)
    check_in_date    = models.DateField()
    check_out_date   = models.DateField()
    nights           = models.PositiveIntegerField(default=1)
    price_per_night  = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount     = models.DecimalField(max_digits=10, decimal_places=2)
    status           = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hotel_bookings'
        ordering = ['-created_at']

    def __str__(self):
        return self.booking_id


class HotelReview(models.Model):
    hotel       = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews')
    tourist     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotel_reviews')
    rating      = models.PositiveIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    review_text = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hotel_reviews'
