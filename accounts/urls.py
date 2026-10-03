from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('',                            RedirectView.as_view(url='/home/', permanent=True)),
    path('home/',                       views.home,                  name='home'),
    path('accounts/register/',          views.register_view,         name='register'),
    path('accounts/login/',             views.login_view,            name='login'),
    path('accounts/logout/',            views.logout_view,           name='logout'),
    path('accounts/forgot-password/',   views.forgot_password_view,  name='forgot_password'),
    path('accounts/reset-password/<str:token>/', views.reset_password_view, name='reset_password'),
    path('dashboard/',                  views.dashboard,             name='dashboard'),
    path('profile/',                    views.profile_view,          name='profile'),
    path('favorites/',                  views.favorites_view,        name='favorites'),
    path('api/toggle-favorite/',        views.toggle_favorite,       name='toggle_favorite'),
]
