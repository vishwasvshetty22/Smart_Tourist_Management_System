from django.urls import path
from . import views

urlpatterns = [
    path('',                                  views.hotel_list,           name='hotel_list'),
    path('my-bookings/',                      views.hotel_booking_history,name='hotel_booking_history'),
    path('cancel/<str:bid>/',                 views.cancel_hotel_booking, name='cancel_hotel_booking'),
    path('hotel-dashboard/',                  views.hotel_dashboard,      name='hotel_dashboard'),
    path('hotel-dashboard/add/',              views.add_hotel,            name='add_hotel'),
    path('hotel-dashboard/<int:hotel_id>/add-room/', views.add_room,      name='add_room'),
    path('hotel-dashboard/room/<int:room_id>/toggle/', views.toggle_room, name='toggle_room'),
    path('hotel-dashboard/booking/<int:booking_id>/<str:action>/', views.manage_hotel_booking, name='manage_hotel_booking'),
    path('<slug:slug>/',                      views.hotel_detail,         name='hotel_detail'),
    path('<slug:slug>/book/',                 views.book_hotel,           name='book_hotel'),
]
