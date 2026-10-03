import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Avg, Q

from .models import Vehicle, VehicleImage, VehicleBooking, VehicleReview
from accounts.models import TouristLocation
from notifications.models import Notification
from payments.emails import send_cancellation_emails



def vehicle_list(request):
    _auto_complete_expired_vehicle_bookings()
    qs = Vehicle.objects.filter(is_approved=True, is_available=True)
    loc  = request.GET.get('location')
    vtyp = request.GET.get('vehicle_type')
    fuel = request.GET.get('fuel_type')
    minp = request.GET.get('min_price')
    maxp = request.GET.get('max_price')
    sort = request.GET.get('sort', '-avg_rating')

    if loc:  qs = qs.filter(location_id=loc)
    if vtyp: qs = qs.filter(vehicle_type=vtyp)
    if fuel: qs = qs.filter(fuel_type=fuel)
    if minp: qs = qs.filter(price_per_day__gte=minp)
    if maxp: qs = qs.filter(price_per_day__lte=maxp)
    qs = qs.order_by(sort)

    paginator = Paginator(qs, 12)
    page_obj  = paginator.get_page(request.GET.get('page'))

    fav_ids = []
    if request.user.is_authenticated:
        from accounts.models import UserFavorite
        fav_ids = list(UserFavorite.objects.filter(user=request.user, item_type='vehicle').values_list('item_id', flat=True))

    return render(request, 'vehicles/vehicle_list.html', {
        'page_obj':      page_obj,
        'locations':     TouristLocation.objects.filter(is_active=True),
        'vehicle_types': Vehicle.TYPE_CHOICES,
        'fuel_types':    Vehicle.FUEL_CHOICES,
        'fav_ids':       fav_ids,
        'total':         qs.count(),
    })


def vehicle_detail(request, pk):
    _auto_complete_expired_vehicle_bookings()
    vehicle  = get_object_or_404(Vehicle, pk=pk, is_approved=True)
    reviews  = vehicle.reviews.order_by('-created_at')[:10]
    similar  = Vehicle.objects.filter(location=vehicle.location, vehicle_type=vehicle.vehicle_type, is_approved=True).exclude(pk=pk)[:4]
    is_fav   = False
    if request.user.is_authenticated:
        from accounts.models import UserFavorite
        is_fav = UserFavorite.objects.filter(user=request.user, item_type='vehicle', item_id=pk).exists()
    return render(request, 'vehicles/vehicle_detail.html', {
        'vehicle': vehicle, 'reviews': reviews,
        'similar': similar, 'is_fav': is_fav,
    })


@login_required
def book_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, is_approved=True, is_available=True)
    if request.method == 'POST':
        start_str = request.POST.get('start_datetime')
        end_str   = request.POST.get('end_datetime')
        rtype     = request.POST.get('rental_type', 'daily')
        pickup    = request.POST.get('pickup_location', '')
        special   = request.POST.get('special_requests', '')

        from django.utils.dateparse import parse_datetime
        start = parse_datetime(start_str)
        end   = parse_datetime(end_str)

        if not start or not end or end <= start:
            messages.error(request, 'Invalid date/time selection.')
            return redirect('vehicle_detail', pk=pk)

        # Check conflict — block against pending (awaiting payment/owner action),
        # confirmed and active bookings, so two tourists can't both pay for the
        # same overlapping slot while one booking is still pending.
        conflict = VehicleBooking.objects.filter(
            vehicle=vehicle, status__in=['pending','confirmed','active'],
            start_datetime__lt=end, end_datetime__gt=start
        ).exists()
        if conflict:
            messages.error(request, 'Vehicle not available for selected dates.')
            return redirect('vehicle_detail', pk=pk)

        hours = (end - start).total_seconds() / 3600
        days  = hours / 24
        if rtype == 'hourly':
            base = float(vehicle.price_per_hour) * hours
        else:
            base = float(vehicle.price_per_day) * max(1, round(days))

        bid = f"VB{timezone.now().strftime('%Y%m%d')}{str(uuid.uuid4().int)[:4]}"
        booking = VehicleBooking.objects.create(
            tourist=request.user, vehicle=vehicle, booking_id=bid,
            rental_type=rtype, start_datetime=start, end_datetime=end,
            pickup_location=pickup, special_requests=special,
            base_amount=round(base, 2),
            security_deposit=vehicle.security_deposit,
            total_amount=round(base + float(vehicle.security_deposit), 2),
        )
        Notification.objects.create(
            user=vehicle.owner, type='new_booking',
            title='New Booking Request',
            message=f"{request.user.get_full_name()} booked your {vehicle.brand} {vehicle.model}.",
        )
        messages.success(request, f'Booking {bid} created! Complete payment to confirm.')
        return redirect('payment_page', booking_type='vehicle', booking_id=bid)

    return redirect('vehicle_detail', pk=pk)


@login_required
def cancel_vehicle_booking(request, bid):
    b = get_object_or_404(VehicleBooking, booking_id=bid, tourist=request.user)
    if b.status not in ['pending', 'confirmed']:
        messages.error(request, 'Cannot cancel this booking.')
        return redirect('vehicle_booking_history')
    if request.method == 'POST':
        b.status = 'cancelled'
        b.cancel_reason = request.POST.get('reason', '')
        b.save()
        Notification.objects.create(
            user=b.vehicle.owner, type='booking_cancelled',
            title='Booking Cancelled', message=f'Booking {bid} cancelled.',
        )
        send_cancellation_emails(b, 'vehicle', b.cancel_reason)
        messages.success(request, 'Booking cancelled.')
        return redirect('vehicle_booking_history')
    return render(request, 'vehicles/cancel_booking.html', {'booking': b})


@login_required
def vehicle_booking_history(request):
    _auto_complete_expired_vehicle_bookings()
    bookings = VehicleBooking.objects.filter(tourist=request.user).order_by('-created_at')
    return render(request, 'vehicles/booking_history.html', {
        'bookings': bookings, 'title': 'My Vehicle Bookings'
    })


# ── Vendor views ──────────────────────────────────────────────────────────────
@login_required
def vendor_dashboard(request):
    if not request.user.is_vehicle_owner:
        messages.error(request, 'Access denied.'); return redirect('home')
    _auto_complete_expired_vehicle_bookings(owner=request.user)
    vehicles = Vehicle.objects.filter(owner=request.user)
    all_bookings = VehicleBooking.objects.filter(vehicle__owner=request.user)
    bookings = all_bookings.order_by('-created_at')[:15]
    from django.db.models import Sum
    earnings = all_bookings.filter(status__in=['confirmed', 'active', 'completed']) \
                           .aggregate(total=Sum('total_amount'))['total'] or 0
    return render(request, 'vehicles/vendor_dashboard.html', {
        'vehicles': vehicles, 'bookings': bookings,
        'stats': {
            'total_vehicles':   vehicles.count(),
            'active_vehicles':  vehicles.filter(is_available=True, is_approved=True).count(),
            'pending_bookings': all_bookings.filter(status='pending').count(),
            'total_earnings':   earnings,
        }
    })


@login_required
def add_vehicle(request):
    if not request.user.is_vehicle_owner:
        messages.error(request, 'Access denied.'); return redirect('home')
    context = {
        'locations':    TouristLocation.objects.filter(is_active=True),
        'type_choices': Vehicle.TYPE_CHOICES,
        'fuel_choices': Vehicle.FUEL_CHOICES,
        'trans_choices': Vehicle.TRANS_CHOICES,
    }
    if request.method == 'POST':
        p = request.POST
        reg_number = p.get('registration_number', '').strip().upper()

        # Validate: registration number must not already exist
        if Vehicle.objects.filter(registration_number=reg_number).exists():
            messages.error(request, f'Registration number "{reg_number}" is already registered in the system. Please check and enter the correct number.')
            context['form_data'] = p
            return render(request, 'vehicles/add_vehicle.html', context)

        # Validate required fields are not empty
        required = ['name', 'vehicle_type', 'brand', 'model', 'year',
                    'registration_number', 'description', 'price_per_hour',
                    'price_per_day', 'pickup_address']
        missing = [f for f in required if not p.get(f, '').strip()]
        if missing:
            messages.error(request, 'Please fill in all required fields.')
            context['form_data'] = p
            return render(request, 'vehicles/add_vehicle.html', context)

        Vehicle.objects.create(
            owner=request.user,
            name=p['name'], vehicle_type=p['vehicle_type'], brand=p['brand'],
            model=p['model'], year=int(p['year']),
            registration_number=reg_number,
            fuel_type=p.get('fuel_type', 'petrol'),
            transmission=p.get('transmission', 'manual'),
            seating_capacity=int(p.get('seating_capacity', 2)),
            description=p['description'],
            features=p.get('features', ''),
            price_per_hour=p['price_per_hour'],
            price_per_day=p['price_per_day'],
            security_deposit=p.get('security_deposit', 0),
            location_id=p.get('location') or None,
            pickup_address=p['pickup_address'],
            thumbnail=request.FILES.get('thumbnail'),
            is_approved=True,
        )
        messages.success(request, 'Vehicle listed successfully! It is now visible to tourists.')
        return redirect('vendor_dashboard')
    return render(request, 'vehicles/add_vehicle.html', context)


@login_required
def manage_booking(request, booking_id, action):
    if not request.user.is_vehicle_owner:
        return JsonResponse({'error':'Forbidden'}, status=403)
    b = get_object_or_404(VehicleBooking, id=booking_id, vehicle__owner=request.user)
    if action == 'accept':
        b.status = 'confirmed'
        msg = f'Booking {b.booking_id} confirmed!'
        ntype = 'booking_confirmed'
    else:
        b.status = 'rejected'
        msg = f'Booking {b.booking_id} was rejected.'
        ntype = 'booking_rejected'
    b.save()
    Notification.objects.create(user=b.tourist, type=ntype, title='Booking Update', message=msg)
    return JsonResponse({'status':'success', 'new_status': b.status})


@login_required
def toggle_vehicle(request, vehicle_id):
    """Vehicle owner manually marks a vehicle as available/unavailable
    (e.g. taking it off the road for servicing), same pattern as hotels' toggle_room."""
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    vehicle.is_available = not vehicle.is_available
    vehicle.save(update_fields=['is_available'])
    messages.success(request, f"{vehicle.brand} {vehicle.model} marked as {'available' if vehicle.is_available else 'unavailable'}.")
    return redirect('vendor_dashboard')


def _auto_complete_expired_vehicle_bookings(owner=None):
    """Bookings whose end_datetime has passed and are still confirmed/active
    are auto-marked completed, freeing up the vehicle for new bookings on
    later dates without any manual action needed."""
    qs = VehicleBooking.objects.filter(status__in=['confirmed','active'], end_datetime__lt=timezone.now())
    if owner is not None:
        qs = qs.filter(vehicle__owner=owner)
    qs.update(status='completed')


def check_availability(request, pk):
    start = request.GET.get('start')
    end   = request.GET.get('end')
    if not start or not end:
        return JsonResponse({'available': False})
    conflict = VehicleBooking.objects.filter(
        vehicle_id=pk, status__in=['pending','confirmed','active'],
        start_datetime__lt=end, end_datetime__gt=start,
    ).exists()
    return JsonResponse({'available': not conflict})


@login_required
def add_review(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    if request.method == 'POST':
        VehicleReview.objects.create(
            vehicle=vehicle, tourist=request.user,
            rating=int(request.POST.get('rating', 5)),
            review_text=request.POST.get('review_text', ''),
        )
        avg = VehicleReview.objects.filter(vehicle=vehicle).aggregate(a=Avg('rating'))['a'] or 0
        vehicle.avg_rating = round(avg, 2)
        vehicle.save()
        messages.success(request, 'Review submitted!')
    return redirect('vehicle_detail', pk=vehicle_id)
