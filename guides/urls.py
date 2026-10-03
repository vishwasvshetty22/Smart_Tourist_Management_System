from django.urls import path
from . import views

urlpatterns = [
    path('',                    views.guide_list,           name='guide_list'),
    path('<int:pk>/',           views.guide_detail,         name='guide_detail'),
    path('<int:pk>/book/',      views.book_guide,           name='book_guide'),
    path('my-bookings/',        views.guide_booking_history,name='guide_booking_history'),
    path('cancel/<str:bid>/',   views.cancel_guide_booking, name='cancel_guide_booking'),
    path('guide-dashboard/',    views.guide_dashboard,      name='guide_dashboard'),
    path('guide-dashboard/toggle/', views.toggle_guide,      name='toggle_guide'),
    path('guide-dashboard/booking/<int:booking_id>/<str:action>/', views.manage_guide_booking, name='manage_guide_booking'),
    path('create-profile/',     views.create_guide_profile, name='create_guide_profile'),
]
