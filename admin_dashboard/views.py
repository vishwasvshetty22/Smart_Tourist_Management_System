from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum
from django.utils import timezone
import functools
from datetime import timedelta
import json

from accounts.models import User, TouristLocation
from vehicles.models import Vehicle, VehicleBooking
from hotels.models import Hotel, HotelBooking
from guides.models import TourGuide, GuideBooking
from payments.models import Payment
from notifications.models import Notification


def admin_required(fn):
    @login_required
    @functools.wraps(fn)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin_user:
            messages.error(request, 'Admin access required.')
            return redirect('home')
        return fn(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_panel(request):
    today      = timezone.now().date()
    last30     = today - timedelta(days=30)

    stats = {
        'total_users':    User.objects.filter(role='tourist').count(),
        'total_vendors':  User.objects.filter(role='vehicle_owner').count(),
        'total_hotels_o': User.objects.filter(role='hotel_owner').count(),
        'total_guides':   TourGuide.objects.count(),
        'total_vehicles': Vehicle.objects.count(),
        'total_hotels':   Hotel.objects.count(),
        'total_vb':       VehicleBooking.objects.count(),
        'total_hb':       HotelBooking.objects.count(),
        'total_gb':       GuideBooking.objects.count(),
        'pending_v':      Vehicle.objects.filter(is_approved=False).count(),
        'pending_h':      Hotel.objects.filter(is_approved=False).count(),
        'pending_g':      TourGuide.objects.filter(is_approved=False).count(),
        'monthly_rev':    Payment.objects.filter(status='success', initiated_at__date__gte=last30)
                                         .aggregate(t=Sum('amount'))['t'] or 0,
        'new_users_30d':  User.objects.filter(date_joined__date__gte=last30).count(),
    }

    # Monthly chart data – last 6 months
    labels, vb_d, hb_d, gb_d = [], [], [], []
    for i in range(5, -1, -1):
        d = (today.replace(day=1) - timedelta(days=i*30))
        labels.append(d.strftime('%b %Y'))
        vb_d.append(VehicleBooking.objects.filter(created_at__year=d.year, created_at__month=d.month).count())
        hb_d.append(HotelBooking.objects.filter(created_at__year=d.year, created_at__month=d.month).count())
        gb_d.append(GuideBooking.objects.filter(created_at__year=d.year, created_at__month=d.month).count())

    location_stats = TouristLocation.objects.annotate(
        v_cnt=Count('vehicles'), h_cnt=Count('hotels')
    ).order_by('-v_cnt')[:6]

    return render(request, 'admin/dashboard.html', {
        'stats':           stats,
        'monthly_labels':  json.dumps(labels),
        'monthly_vb':      json.dumps(vb_d),
        'monthly_hb':      json.dumps(hb_d),
        'monthly_gb':      json.dumps(gb_d),
        'location_stats':  location_stats,
        'recent_vb':       VehicleBooking.objects.select_related('tourist','vehicle').order_by('-created_at')[:6],
        'recent_users':    User.objects.order_by('-date_joined')[:5],
        'pending_vehicles':Vehicle.objects.filter(is_approved=False).select_related('owner','location')[:10],
        'pending_hotels':  Hotel.objects.filter(is_approved=False).select_related('owner','location')[:10],
        'pending_guides':  TourGuide.objects.filter(is_approved=False).select_related('user')[:10],
    })


@admin_required
def admin_approvals(request):
    """Dedicated approvals page — unlike the dashboard's pending-items widgets
    (which disappear entirely once nothing is pending, making the sidebar's
    Approvals links look broken), this page always renders all three
    sections so the link always lands somewhere meaningful."""
    return render(request, 'admin/approvals.html', {
        'pending_vehicles': Vehicle.objects.filter(is_approved=False).select_related('owner', 'location').order_by('-created_at'),
        'pending_hotels':   Hotel.objects.filter(is_approved=False).select_related('owner', 'location').order_by('-created_at'),
        'pending_guides':   TourGuide.objects.filter(is_approved=False).select_related('user').order_by('-created_at'),
    })


@admin_required
def manage_users(request):
    role   = request.GET.get('role', '')
    search = request.GET.get('q', '')
    qs     = User.objects.all().order_by('-date_joined')
    if role:   qs = qs.filter(role=role)
    if search: qs = qs.filter(first_name__icontains=search) | qs.filter(email__icontains=search)

    from django.core.paginator import Paginator
    page_obj = Paginator(qs, 20).get_page(request.GET.get('page'))
    return render(request, 'admin/manage_users.html', {
        'page_obj': page_obj, 'search': search, 'role_filter': role,
        'roles': User.ROLE_CHOICES,
    })


@admin_required
def toggle_block(request, user_id):
    u = get_object_or_404(User, pk=user_id)
    u.is_blocked = not u.is_blocked
    u.save()
    return JsonResponse({'status': 'blocked' if u.is_blocked else 'unblocked'})


@admin_required
def approve_vehicle(request, vid):
    v = get_object_or_404(Vehicle, pk=vid)
    v.is_approved = True; v.save()
    Notification.objects.create(user=v.owner, type='listing_approved',
        title='Vehicle Approved!', message=f'Your {v.brand} {v.model} is now live.')
    messages.success(request, f'{v} approved.')
    return redirect(request.POST.get('next') or request.GET.get('next') or 'admin_approvals')


@admin_required
def approve_hotel(request, hid):
    h = get_object_or_404(Hotel, pk=hid)
    h.is_approved = True; h.save()
    Notification.objects.create(user=h.owner, type='listing_approved',
        title='Hotel Approved!', message=f'{h.name} is now live.')
    messages.success(request, f'{h} approved.')
    return redirect(request.POST.get('next') or request.GET.get('next') or 'admin_approvals')


@admin_required
def approve_guide(request, gid):
    g = get_object_or_404(TourGuide, pk=gid)
    g.is_approved = True; g.save()
    Notification.objects.create(user=g.user, type='listing_approved',
        title='Guide Profile Approved!', message='Your guide profile is now live.')
    messages.success(request, f'{g} approved.')
    return redirect(request.POST.get('next') or request.GET.get('next') or 'admin_approvals')


@admin_required
def admin_bookings(request):
    btype    = request.GET.get('type', 'vehicle')
    bookings = None
    if btype == 'vehicle':
        bookings = VehicleBooking.objects.select_related('tourist','vehicle').order_by('-created_at')
    elif btype == 'hotel':
        bookings = HotelBooking.objects.select_related('tourist','hotel','room').order_by('-created_at')
    else:
        bookings = GuideBooking.objects.select_related('tourist','guide').order_by('-created_at')

    from django.core.paginator import Paginator
    page_obj = Paginator(bookings, 20).get_page(request.GET.get('page'))
    return render(request, 'admin/bookings.html', {'page_obj': page_obj, 'btype': btype})


@admin_required
def analytics_api(request):
    today = timezone.now().date()
    labels, rev = [], []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        labels.append(d.strftime('%d %b'))
        r = Payment.objects.filter(status='success', initiated_at__date=d).aggregate(t=Sum('amount'))['t'] or 0
        rev.append(float(r))
    return JsonResponse({'revenue_labels': labels, 'revenue_data': rev})
