from django.urls import path
from . import views

urlpatterns = [
    path('trip-planner/',               views.trip_planner,       name='trip_planner'),
    path('my-plans/',                   views.my_trip_plans,      name='my_trip_plans'),
    path('chatbot/',                    views.chatbot_api,         name='chatbot_api'),
    path('weather/',                    views.weather_api,         name='weather_api'),
    path('emergency/<int:location_id>/',views.emergency_contacts,  name='emergency_contacts'),
]
