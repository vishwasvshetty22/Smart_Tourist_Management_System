import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator

from .models import Hotel, HotelRoom, HotelBooking, HotelReview
from accounts.models import TouristLocation
from notifications.models import Notification
from payments.emails import send_cancellation_emails


def _auto_checkout_expired_hotel_bookings(owner=None):
    """Bookings whose check_out_date has passed and are still confirmed/checked_in
    are auto-marked checked_out, so the room's booking history reflects reality
    and the date range frees up for new bookings without manual action."""
    from datetime import date
    qs = HotelBooking.objects.filter(status__in=['confirmed', 'checked_in'], check_out_date__lt=date.today())
    if owner is not None:
        qs = qs.filter(hotel__owner=owner)
    qs.update(status='checked_out')


def hotel_list(request):
    qs = Hotel.objects.filter(is_approved=True)
    loc  = request.GET.get('location')
    cat  = request.GET.get('category')
    minp = request.GET.get('min_price')
    maxp = request.GET.get('max_price')
    sort = request.GET.get('sort', '-avg_rating')

    if loc:  qs = qs.filter(location_id=loc)
    if cat:  qs = qs.filter(category=cat)
    if minp: qs = qs.filter(rooms__price_per_night__gte=minp)
    if maxp: qs = qs.filter(rooms__price_per_night__lte=maxp)
    qs = qs.distinct().order_by(sort)

    paginator = Paginator(qs, 12)
    page_obj  = paginator.get_page(request.GET.get('page'))
    return render(request, 'hotels/hotel_list.html', {
        'page_obj': page_obj,
        'locations': TouristLocation.objects.filter(is_active=True),
        'categories': Hotel.CAT,
        'selected_location': loc,
    })


def hotel_detail(request, slug):
    _auto_checkout_expired_hotel_bookings()
    hotel   = get_object_or_404(Hotel, slug=slug, is_approved=True)
    rooms   = hotel.rooms.filter(is_available=True)
    reviews = hotel.reviews.order_by('-created_at')[:10]
    return render(request, 'hotels/hotel_detail.html', {
        'hotel': hotel, 'rooms': rooms, 'reviews': reviews
    })


@login_required
def book_hotel(request, slug):
    hotel = get_object_or_404(Hotel, slug=slug, is_approved=True)
    if request.method == 'POST':
        p    = request.POST
        room = HotelRoom.objects.filter(id=p.get('room_id'), hotel=hotel, is_available=True).first()
        if not room:
            messages.error(request, 'Selected room is not available.')
            return redirect('hotel_detail', slug=slug)

        from datetime import date
        try:
            ci = date.fromisoformat(p['check_in_date'])
            co = date.fromisoformat(p['check_out_date'])
        except (KeyError, ValueError):
            messages.error(request, 'Please select valid check-in and check-out dates.')
            return redirect('hotel_detail', slug=slug)

        if co <= ci:
            messages.error(request, 'Check-out date must be after check-in date.')
            return redirect('hotel_detail', slug=slug)

        # Prevent double-booking the same room for overlapping dates
        conflict = HotelBooking.objects.filter(
            room=room, status__in=['pending', 'confirmed', 'checked_in'],
            check_in_date__lt=co, check_out_date__gt=ci,
        ).exists()
        if conflict:
            messages.error(request, 'This room is already booked for the selected dates.')
            return redirect('hotel_detail', slug=slug)

        nights = max(1, (co - ci).days)
        total  = float(room.price_per_night) * nights
        bid    = f"HB{timezone.now().strftime('%Y%m%d')}{str(uuid.uuid4().int)[:4]}"

        booking = HotelBooking.objects.create(
            tourist=request.user, hotel=hotel, room=room, booking_id=bid,
            guests_count=int(p.get('guests_count', 1)),
            guest_name=p.get('guest_name', request.user.get_full_name()),
            guest_phone=p.get('guest_phone', request.user.phone),
            special_requests=p.get('special_requests', ''),
            check_in_date=ci, check_out_date=co,
            nights=nights, price_per_night=room.price_per_night, total_amount=total,
        )
        Notification.objects.create(
            user=hotel.owner, type='new_booking',
            title='New Hotel Booking',
            message=f"{request.user.get_full_name()} booked Room {room.room_number} at {hotel.name}.",
        )
        messages.success(request, f'Booking {bid} created!')
        return redirect('payment_page', booking_type='hotel', booking_id=bid)
    return redirect('hotel_detail', slug=slug)


@login_required
def hotel_booking_history(request):
    _auto_checkout_expired_hotel_bookings()
    bookings = HotelBooking.objects.filter(tourist=request.user).order_by('-created_at')
    return render(request, 'hotels/booking_history.html', {
        'bookings': bookings, 'title': 'My Hotel Bookings'
    })


@login_required
def hotel_dashboard(request):
    if not request.user.is_hotel_owner:
        messages.error(request, 'Access denied.'); return redirect('home')
    _auto_checkout_expired_hotel_bookings(owner=request.user)
    hotels   = Hotel.objects.filter(owner=request.user).prefetch_related('rooms')
    all_bookings = HotelBooking.objects.filter(hotel__owner=request.user)
    bookings = all_bookings.order_by('-created_at')[:15]

    from django.db.models import Sum
    from .models import HotelRoom
    
    total_rooms = HotelRoom.objects.filter(hotel__owner=request.user).count()
    earnings = all_bookings.filter(status__in=['confirmed', 'checked_in', 'checked_out']) \
                           .aggregate(total=Sum('total_amount'))['total'] or 0

    stats = {
        'total_hotels':     hotels.count(),
        'total_rooms':      total_rooms,
        'pending_bookings': all_bookings.filter(status='pending').count(),
        'total_earnings':   earnings,
    }

    return render(request, 'hotels/hotel_dashboard.html', {
        'hotels': hotels, 'bookings': bookings, 'stats': stats,
    })


@login_required
def add_hotel(request):
    if not request.user.is_hotel_owner:
        messages.error(request, 'Access denied.'); return redirect('home')
    if request.method == 'POST':
        from django.utils.text import slugify
        p    = request.POST
        name = p['name']
        slug = slugify(name)
        # Make slug unique
        base, n = slug, 1
        while Hotel.objects.filter(slug=slug).exists():
            slug = f"{base}-{n}"; n += 1

        hotel = Hotel.objects.create(
            owner=request.user, name=name, slug=slug,
            category=p.get('category','standard'),
            description=p['description'],
            star_rating=int(p.get('star_rating',3)),
            location_id=p.get('location') or None,
            address=p['address'], city=p['city'], state=p['state'],
            amenities=p.get('amenities',''),
            phone=p['phone'], email=p.get('email',''),
            thumbnail=request.FILES.get('thumbnail'),
            is_approved=True,
        )
        messages.success(request, 'Hotel listed successfully! It is now visible to tourists.')
        return redirect('hotel_dashboard')
    return render(request, 'hotels/add_hotel.html', {
        'locations': TouristLocation.objects.filter(is_active=True),
        'categories': Hotel.CAT,
    })


@login_required
def add_room(request, hotel_id):
    """Hotel owner adds a room to one of their own hotels.
    Without this, owners have no way to create bookable rooms,
    so tourists can never book (hotel.rooms stays empty)."""
    hotel = get_object_or_404(Hotel, id=hotel_id, owner=request.user)
    if request.method == 'POST':
        p = request.POST
        required = ['room_type', 'room_number', 'price_per_night']
        missing = [f for f in required if not p.get(f, '').strip()]
        if missing:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'hotels/add_room.html', {
                'hotel': hotel, 'room_types': HotelRoom.TYPES, 'form_data': p,
            })

        HotelRoom.objects.create(
            hotel=hotel,
            room_type=p['room_type'],
            room_number=p['room_number'].strip(),
            capacity=int(p.get('capacity', 2)),
            price_per_night=p['price_per_night'],
            amenities=p.get('amenities', ''),
            has_ac=bool(p.get('has_ac')),
            has_wifi=bool(p.get('has_wifi')),
            thumbnail=request.FILES.get('thumbnail'),
            is_available=True,
        )
        messages.success(request, f"Room {p['room_number']} added to {hotel.name}! It's now bookable.")
        return redirect('hotel_dashboard')

    return render(request, 'hotels/add_room.html', {
        'hotel': hotel, 'room_types': HotelRoom.TYPES,
    })


@login_required
def toggle_room(request, room_id):
    """Hotel owner marks a room as available/unavailable."""
    room = get_object_or_404(HotelRoom, id=room_id, hotel__owner=request.user)
    room.is_available = not room.is_available
    room.save()
    messages.success(request, f"Room {room.room_number} marked as {'available' if room.is_available else 'unavailable'}.")
    return redirect('hotel_dashboard')


@login_required
def manage_hotel_booking(request, booking_id, action):
    """Hotel owner confirms or cancels a pending booking."""
    if not request.user.is_hotel_owner:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    b = get_object_or_404(HotelBooking, id=booking_id, hotel__owner=request.user)
    if action == 'confirm':
        b.status = 'confirmed'
        msg = f'Your booking {b.booking_id} at {b.hotel.name} was confirmed!'
        ntype = 'booking_confirmed'
        b.hotel.total_bookings += 1
        b.hotel.save(update_fields=['total_bookings'])
    else:
        b.status = 'cancelled'
        msg = f'Your booking {b.booking_id} at {b.hotel.name} was cancelled by the hotel.'
        ntype = 'booking_cancelled'
    b.save()
    Notification.objects.create(user=b.tourist, type=ntype, title='Booking Update', message=msg)
    return JsonResponse({'status': 'success', 'new_status': b.status})


@login_required
def cancel_hotel_booking(request, bid):
    b = get_object_or_404(HotelBooking, booking_id=bid, tourist=request.user)
    if b.status not in ['pending', 'confirmed']:
        messages.error(request, 'Cannot cancel this booking.')
        return redirect('hotel_booking_history')
    if request.method == 'POST':
        b.status = 'cancelled'
        b.save()
        reason = request.POST.get('reason', '')
        Notification.objects.create(
            user=b.hotel.owner, type='booking_cancelled',
            title='Booking Cancelled', message=f'Booking {bid} at {b.hotel.name} was cancelled by the customer.',
        )
        send_cancellation_emails(b, 'hotel', reason)
        messages.success(request, 'Booking cancelled successfully.')
        return redirect('hotel_booking_history')
    return render(request, 'hotels/cancel_booking.html', {'booking': b})
