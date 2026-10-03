import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator

from .models import TourGuide, GuideBooking
from accounts.models import TouristLocation
from notifications.models import Notification
from payments.emails import send_cancellation_emails


def guide_list(request):
    _auto_complete_expired_guide_bookings()
    qs   = TourGuide.objects.filter(is_approved=True, is_available=True)
    loc  = request.GET.get('location')
    exp  = request.GET.get('expertise')
    sort = request.GET.get('sort', '-avg_rating')
    if loc: qs = qs.filter(locations__id=loc)
    if exp: qs = qs.filter(expertise=exp)
    qs = qs.order_by(sort)
    paginator = Paginator(qs, 12)
    page_obj  = paginator.get_page(request.GET.get('page'))
    return render(request, 'guides/guide_list.html', {
        'page_obj': page_obj,
        'locations': TouristLocation.objects.filter(is_active=True),
        'expertise_choices': TourGuide.EXPERTISE,
    })


def guide_detail(request, pk):
    _auto_complete_expired_guide_bookings()
    guide   = get_object_or_404(TourGuide, pk=pk, is_approved=True)
    reviews = guide.reviews.order_by('-created_at')[:10]
    return render(request, 'guides/guide_detail.html', {
        'guide': guide, 'reviews': reviews
    })


@login_required
def book_guide(request, pk):
    guide = get_object_or_404(TourGuide, pk=pk, is_approved=True, is_available=True)
    if request.method == 'POST':
        p    = request.POST
        from django.utils.dateparse import parse_datetime
        start = parse_datetime(p['start_datetime'])
        end   = parse_datetime(p['end_datetime'])

        if not start or not end or end <= start:
            messages.error(request, 'Please select a valid start and end date/time.')
            return redirect('guide_detail', pk=pk)

        # Prevent double-booking the same guide for overlapping dates/times.
        # Block against pending (awaiting payment/guide action), confirmed,
        # so two tourists can't both pay for the same overlapping slot.
        conflict = GuideBooking.objects.filter(
            guide=guide, status__in=['pending', 'confirmed'],
            start_datetime__lt=end, end_datetime__gt=start,
        ).exists()
        if conflict:
            messages.error(request, 'This guide is already booked for the selected date/time.')
            return redirect('guide_detail', pk=pk)

        btype = p.get('booking_type', 'daily')
        hours = (end - start).total_seconds() / 3600
        days  = max(1, round(hours / 24))
        total = float(guide.price_per_hour) * hours if btype == 'hourly' else float(guide.price_per_day) * days
        bid   = f"GB{timezone.now().strftime('%Y%m%d')}{str(uuid.uuid4().int)[:4]}"

        GuideBooking.objects.create(
            tourist=request.user, guide=guide, booking_id=bid,
            location_id=p.get('location') or None,
            booking_type=btype, start_datetime=start, end_datetime=end,
            meeting_point=p.get('meeting_point', ''),
            group_size=int(p.get('group_size', 1)),
            special_requests=p.get('special_requests', ''),
            total_amount=round(total, 2),
        )
        Notification.objects.create(
            user=guide.user, type='new_booking',
            title='New Tour Booking',
            message=f"{request.user.get_full_name()} booked a tour with you.",
        )
        messages.success(request, f'Guide booked! Booking ID: {bid}')
        return redirect('payment_page', booking_type='guide', booking_id=bid)
    return redirect('guide_detail', pk=pk)


@login_required
def guide_booking_history(request):
    _auto_complete_expired_guide_bookings()
    bookings = GuideBooking.objects.filter(tourist=request.user).order_by('-created_at')
    return render(request, 'guides/booking_history.html', {
        'bookings': bookings, 'title': 'My Guide Bookings'
    })


@login_required
def guide_dashboard(request):
    if not request.user.is_guide:
        messages.error(request, 'Access denied.'); return redirect('home')
    try:
        guide = request.user.guide_profile
        _auto_complete_expired_guide_bookings(guide=guide)
        all_bookings = GuideBooking.objects.filter(guide=guide)
        bookings = all_bookings.order_by('-created_at')[:15]

        from django.db.models import Sum
        earnings = all_bookings.filter(status__in=['confirmed', 'completed']) \
                               .aggregate(total=Sum('total_amount'))['total'] or 0

        stats = {
            'pending_bookings': all_bookings.filter(status='pending').count(),
            'total_earnings':   earnings,
        }

        return render(request, 'guides/guide_dashboard.html', {
            'guide': guide, 'bookings': bookings, 'stats': stats,
        })
    except TourGuide.DoesNotExist:
        return redirect('create_guide_profile')


@login_required
def manage_guide_booking(request, booking_id, action):
    """Guide accepts or rejects a pending booking request."""
    if not request.user.is_guide:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    b = get_object_or_404(GuideBooking, id=booking_id, guide__user=request.user)
    if action == 'accept':
        b.status = 'confirmed'
        msg = f'Your booking {b.booking_id} with {b.guide.name} was confirmed!'
        ntype = 'booking_confirmed'
    else:
        b.status = 'rejected'
        msg = f'Your booking {b.booking_id} with {b.guide.name} was rejected.'
        ntype = 'booking_rejected'
    b.save()
    Notification.objects.create(user=b.tourist, type=ntype, title='Booking Update', message=msg)
    return JsonResponse({'status': 'success', 'new_status': b.status})


@login_required
def toggle_guide(request):
    """Guide manually marks themselves as available/unavailable for new bookings."""
    if not request.user.is_guide:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    guide = get_object_or_404(TourGuide, user=request.user)
    guide.is_available = not guide.is_available
    guide.save(update_fields=['is_available'])
    messages.success(request, f"You are now marked as {'available' if guide.is_available else 'unavailable'} for new bookings.")
    return redirect('guide_dashboard')


def _auto_complete_expired_guide_bookings(guide=None):
    """Bookings whose end_datetime has passed and are still confirmed
    are auto-marked completed, freeing up the guide for new bookings."""
    qs = GuideBooking.objects.filter(status='confirmed', end_datetime__lt=timezone.now())
    if guide is not None:
        qs = qs.filter(guide=guide)
    qs.update(status='completed')


@login_required
def create_guide_profile(request):
    if not request.user.is_guide:
        return redirect('home')
    if hasattr(request.user, 'guide_profile'):
        return redirect('guide_dashboard')
    if request.method == 'POST':
        p = request.POST
        g = TourGuide.objects.create(
            user=request.user,
            years_experience=int(p.get('years_experience', 1)),
            expertise=p.get('expertise', 'general'),
            bio=p['bio'],
            languages=p['languages'],
            price_per_hour=p['price_per_hour'],
            price_per_day=p['price_per_day'],
            profile_image=request.FILES.get('profile_image'),
            is_approved=True,
        )
        location_ids = request.POST.getlist('locations')
        if location_ids:
            g.locations.set(TouristLocation.objects.filter(id__in=location_ids))
        messages.success(request, 'Profile created successfully! You are now visible to tourists.')
        return redirect('guide_dashboard')
    return render(request, 'guides/create_profile.html', {
        'locations':  TouristLocation.objects.filter(is_active=True),
        'expertise':  TourGuide.EXPERTISE,
    })


@login_required
def cancel_guide_booking(request, bid):
    b = get_object_or_404(GuideBooking, booking_id=bid, tourist=request.user)
    if b.status not in ['pending', 'confirmed']:
        messages.error(request, 'Cannot cancel this booking.')
        return redirect('guide_booking_history')
    if request.method == 'POST':
        b.status = 'cancelled'
        b.save()
        reason = request.POST.get('reason', '')
        Notification.objects.create(
            user=b.guide.user, type='booking_cancelled',
            title='Booking Cancelled', message=f'Booking {bid} was cancelled by the customer.',
        )
        send_cancellation_emails(b, 'guide', reason)
        messages.success(request, 'Booking cancelled successfully.')
        return redirect('guide_booking_history')
    return render(request, 'guides/cancel_booking.html', {'booking': b})
