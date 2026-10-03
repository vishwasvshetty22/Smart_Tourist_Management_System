import secrets
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings

from .models import User, TouristLocation, UserFavorite, PasswordResetToken
from .forms import RegisterForm, LoginForm, ProfileForm, ForgotPasswordForm, ResetPasswordForm


def home(request):
    from vehicles.models import Vehicle
    from hotels.models import Hotel
    from guides.models import TourGuide
    locations        = TouristLocation.objects.filter(is_active=True)
    feat_vehicles    = Vehicle.objects.filter(is_approved=True, is_featured=True)[:6]
    feat_hotels      = Hotel.objects.filter(is_approved=True, is_featured=True)[:6]
    feat_guides      = TourGuide.objects.filter(is_approved=True, is_featured=True)[:4]
    return render(request, 'home.html', {
        'locations': locations,
        'feat_vehicles': feat_vehicles,
        'feat_hotels': feat_hotels,
        'feat_guides': feat_guides,
        'total_vehicles': Vehicle.objects.filter(is_approved=True).count(),
        'total_hotels':   Hotel.objects.filter(is_approved=True).count(),
        'total_guides':   TourGuide.objects.filter(is_approved=True).count(),
    })


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cd   = form.cleaned_data
        user = User(
            email=cd['email'], username=cd['username'],
            first_name=cd['first_name'], last_name=cd['last_name'],
            phone=cd.get('phone',''), role=cd['role'], is_verified=True,
        )
        user.set_password(cd['password'])
        user.save()
        messages.success(request, 'Account created! Please login.')
        return redirect('login')
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(request, email=form.cleaned_data['email'], password=form.cleaned_data['password'])
        if user:
            if user.is_blocked:
                messages.error(request, 'Your account is blocked. Contact support.')
            else:
                login(request, user)
                return redirect(request.GET.get('next', 'dashboard'))
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')


@login_required
def dashboard(request):
    u = request.user
    if u.is_vehicle_owner: return redirect('vendor_dashboard')
    if u.is_hotel_owner:   return redirect('hotel_dashboard')
    if u.is_guide:         return redirect('guide_dashboard')
    if u.is_admin_user:    return redirect('admin_panel')
    return tourist_dashboard(request)


@login_required
def tourist_dashboard(request):
    from vehicles.models import VehicleBooking
    from hotels.models import HotelBooking
    from guides.models import GuideBooking
    from notifications.models import Notification
    u = request.user
    return render(request, 'accounts/tourist_dashboard.html', {
        'vehicle_bookings': VehicleBooking.objects.filter(tourist=u).order_by('-created_at')[:5],
        'hotel_bookings':   HotelBooking.objects.filter(tourist=u).order_by('-created_at')[:5],
        'guide_bookings':   GuideBooking.objects.filter(tourist=u).order_by('-created_at')[:5],
        'total_vb':   VehicleBooking.objects.filter(tourist=u).count(),
        'total_hb':   HotelBooking.objects.filter(tourist=u).count(),
        'total_gb':   GuideBooking.objects.filter(tourist=u).count(),
        'unread':     Notification.objects.filter(user=u, is_read=False).count(),
    })


@login_required
def profile_view(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated!')
        return redirect('profile')
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def favorites_view(request):
    from vehicles.models import Vehicle
    from hotels.models import Hotel
    from guides.models import TourGuide
    favs = UserFavorite.objects.filter(user=request.user)
    veh, htl, gde = [], [], []
    for f in favs:
        try:
            if f.item_type == 'vehicle': veh.append(Vehicle.objects.get(id=f.item_id))
            elif f.item_type == 'hotel': htl.append(Hotel.objects.get(id=f.item_id))
            elif f.item_type == 'guide': gde.append(TourGuide.objects.get(id=f.item_id))
        except Exception:
            pass
    return render(request, 'accounts/favorites.html', {'fav_vehicles':veh,'fav_hotels':htl,'fav_guides':gde})


@login_required
def toggle_favorite(request):
    if request.method != 'POST':
        return JsonResponse({'error':'POST only'}, status=405)
    item_type = request.POST.get('item_type')
    item_id   = request.POST.get('item_id')
    fav, created = UserFavorite.objects.get_or_create(
        user=request.user, item_type=item_type, item_id=item_id)
    if not created:
        fav.delete()
        return JsonResponse({'status':'removed'})
    return JsonResponse({'status':'added'})


# ── Forgot / Reset Password ───────────────────────────────────────────────────

def forgot_password_view(request):
    """Step 1: User enters email to receive reset link."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = ForgotPasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        user  = User.objects.get(email=email)

        # Invalidate old tokens
        PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)

        # Create new token
        token = secrets.token_urlsafe(32)
        PasswordResetToken.objects.create(user=user, token=token)

        reset_url = request.build_absolute_uri(f'/accounts/reset-password/{token}/')

        # Send email (prints to console in dev mode)
        send_mail(
            subject='SmartTourist – Password Reset Request',
            message=(
                f'Hi {user.get_full_name()},\n\n'
                f'You requested a password reset for your SmartTourist account.\n\n'
                f'Click the link below to reset your password (valid for 1 hour):\n{reset_url}\n\n'
                f'If you did not request this, please ignore this email.\n\n'
                f'– SmartTourist Team'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        messages.success(request,
            'Password reset link sent! Check your email (or console in dev mode).')
        return redirect('login')
    return render(request, 'accounts/forgot_password.html', {'form': form})


def reset_password_view(request, token):
    """Step 2: User clicks link from email and sets a new password."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    try:
        reset_obj = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid or expired reset link.')
        return redirect('forgot_password')

    if not reset_obj.is_valid():
        messages.error(request, 'This reset link has expired or already been used. Please request a new one.')
        return redirect('forgot_password')

    form = ResetPasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = reset_obj.user
        user.set_password(form.cleaned_data['password'])
        user.save()
        reset_obj.is_used = True
        reset_obj.save()
        messages.success(request, 'Password reset successfully! You can now log in with your new password.')
        return redirect('login')

    return render(request, 'accounts/reset_password.html', {'form': form, 'token': token})
