from django.urls import path
from . import views

urlpatterns = [
    path('pay/<str:booking_type>/<str:booking_id>/', views.payment_page,     name='payment_page'),
    path('complete/',                                views.complete_payment,  name='complete_payment'),
]
