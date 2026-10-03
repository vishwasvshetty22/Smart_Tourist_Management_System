from django.urls import path
from . import views

urlpatterns = [
    path('',                                    views.vehicle_list,           name='vehicle_list'),
    path('<int:pk>/',                           views.vehicle_detail,         name='vehicle_detail'),
    path('<int:pk>/book/',                      views.book_vehicle,           name='book_vehicle'),
    path('<int:pk>/availability/',              views.check_availability,     name='check_availability'),
    path('<int:vehicle_id>/review/',            views.add_review,             name='add_vehicle_review'),
    path('my-bookings/',                        views.vehicle_booking_history,name='vehicle_booking_history'),
    path('cancel/<str:bid>/',                   views.cancel_vehicle_booking, name='cancel_vehicle_booking'),
    path('vendor/dashboard/',                   views.vendor_dashboard,       name='vendor_dashboard'),
    path('vendor/add/',                         views.add_vehicle,            name='add_vehicle'),
    path('vendor/<int:vehicle_id>/toggle/',     views.toggle_vehicle,         name='toggle_vehicle'),
    path('vendor/booking/<int:booking_id>/<str:action>/', views.manage_booking, name='manage_booking'),
]
