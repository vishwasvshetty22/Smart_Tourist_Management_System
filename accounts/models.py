from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError('Email required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        extra.setdefault('role', 'admin')
        return self.create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('tourist',       'Tourist'),
        ('vehicle_owner', 'Vehicle Owner'),
        ('hotel_owner',   'Hotel Owner'),
        ('guide',         'Tour Guide'),
        ('admin',         'Admin'),
    ]
    email           = models.EmailField(unique=True)
    username        = models.CharField(max_length=150, unique=True)
    first_name      = models.CharField(max_length=100)
    last_name       = models.CharField(max_length=100)
    phone           = models.CharField(max_length=15, blank=True)
    role            = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tourist')
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio             = models.TextField(blank=True)
    address         = models.TextField(blank=True)
    city            = models.CharField(max_length=100, blank=True)
    state           = models.CharField(max_length=100, blank=True)
    is_active       = models.BooleanField(default=True)
    is_staff        = models.BooleanField(default=False)
    is_verified     = models.BooleanField(default=False)
    is_blocked      = models.BooleanField(default=False)
    date_joined     = models.DateTimeField(default=timezone.now)
    updated_at      = models.DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_tourist(self):       return self.role == 'tourist'
    @property
    def is_vehicle_owner(self): return self.role == 'vehicle_owner'
    @property
    def is_hotel_owner(self):   return self.role == 'hotel_owner'
    @property
    def is_guide(self):         return self.role == 'guide'
    @property
    def is_admin_user(self):    return self.role == 'admin'


class TouristLocation(models.Model):
    name        = models.CharField(max_length=100)
    slug        = models.SlugField(unique=True)
    state       = models.CharField(max_length=100)
    description = models.TextField()
    image       = models.ImageField(upload_to='locations/', null=True, blank=True)
    latitude    = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude   = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    best_season = models.CharField(max_length=100, blank=True)
    activities  = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tourist_locations'

    def __str__(self):
        return self.name


class UserFavorite(models.Model):
    ITEM_TYPES = [('vehicle','Vehicle'),('hotel','Hotel'),('guide','Guide')]
    user      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    item_id   = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'favorites'
        unique_together = ['user', 'item_type', 'item_id']


class PasswordResetToken(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
    token      = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used    = models.BooleanField(default=False)

    class Meta:
        db_table = 'password_reset_tokens'

    def is_valid(self):
        from django.utils import timezone
        from datetime import timedelta
        return not self.is_used and (timezone.now() - self.created_at) < timedelta(hours=1)

    def __str__(self):
        return f"Reset token for {self.user.email}"
