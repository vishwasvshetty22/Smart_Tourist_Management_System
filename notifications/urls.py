from django.urls import path
from . import views
urlpatterns = [
    path('',              views.notifications_list, name='notifications_list'),
    path('unread-count/', views.unread_count,       name='unread_count'),
    path('mark-read/',    views.mark_all_read,      name='mark_all_read'),
]

