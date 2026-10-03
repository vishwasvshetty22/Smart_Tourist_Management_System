from django.contrib import admin
from .models import ChatbotQuery, TripPlan, EmergencyContact

@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ['name','phone','type','location','is_active']
    list_editable = ['is_active']

admin.site.register(ChatbotQuery)
admin.site.register(TripPlan)
