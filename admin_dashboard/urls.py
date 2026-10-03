from django.urls import path
from . import views

urlpatterns = [
    path('',                           views.admin_panel,    name='admin_panel'),
    path('approvals/',                 views.admin_approvals,name='admin_approvals'),
    path('users/',                     views.manage_users,   name='admin_users'),
    path('users/<int:user_id>/block/', views.toggle_block,   name='toggle_block'),
    path('approve/vehicle/<int:vid>/', views.approve_vehicle,name='approve_vehicle'),
    path('approve/hotel/<int:hid>/',   views.approve_hotel,  name='approve_hotel'),
    path('approve/guide/<int:gid>/',   views.approve_guide,  name='approve_guide'),
    path('bookings/',                  views.admin_bookings, name='admin_bookings'),
    path('api/analytics/',             views.analytics_api,  name='analytics_api'),
]
