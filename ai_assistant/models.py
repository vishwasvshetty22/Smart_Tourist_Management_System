from django.db import models
from accounts.models import User, TouristLocation


class ChatbotQuery(models.Model):
    user         = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='chatbot_queries')
    session_id   = models.CharField(max_length=100)
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chatbot_queries'
        ordering = ['timestamp']


class TripPlan(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trip_plans')
    location    = models.ForeignKey(TouristLocation, on_delete=models.SET_NULL, null=True)
    budget      = models.DecimalField(max_digits=10, decimal_places=2)
    num_days    = models.PositiveIntegerField()
    num_people  = models.PositiveIntegerField(default=1)
    preferences = models.TextField(blank=True)
    itinerary   = models.JSONField(default=dict)
    hotel_suggestions   = models.JSONField(default=list)
    vehicle_suggestions = models.JSONField(default=list)
    cost_breakdown      = models.JSONField(default=dict)
    tips        = models.JSONField(default=list)
    title       = models.CharField(max_length=200, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'trip_plans'
        ordering = ['-created_at']


class EmergencyContact(models.Model):
    TYPES = [('police','Police'),('hospital','Hospital'),('fire','Fire'),
             ('ambulance','Ambulance'),('tourist_helpline','Tourist Helpline')]
    location  = models.ForeignKey(TouristLocation, on_delete=models.CASCADE, related_name='emergency_contacts')
    name      = models.CharField(max_length=200)
    phone     = models.CharField(max_length=20)
    type      = models.CharField(max_length=30, choices=TYPES)
    address   = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'emergency_contacts'
