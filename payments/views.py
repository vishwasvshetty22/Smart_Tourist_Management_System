import uuid
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from .models import Payment
from notifications.models import Notification
from .emails import send_booking_emails

logger = logging.getLogger(__name__)



@login_required
def payment_page(request, booking_type, booking_id):
    """Show payment page with booking summary."""
    booking = None
    amount  = 0

    if booking_type == 'vehicle':
        from vehicles.models import VehicleBooking
        booking = get_object_or_404(VehicleBooking, booking_id=booking_id, tourist=request.user)
        amount  = booking.total_amount
    elif booking_type == 'hotel':
        from hotels.models import HotelBooking
        booking = get_object_or_404(HotelBooking, booking_id=booking_id, tourist=request.user)
        amount  = booking.total_amount
    elif booking_type == 'guide':
        from guides.models import GuideBooking
        booking = get_object_or_404(GuideBooking, booking_id=booking_id, tourist=request.user)
        amount  = booking.total_amount

    return render(request, 'payments/payment_page.html', {
        'booking': booking,
        'booking_type': booking_type,
        'booking_id': booking_id,
        'amount': amount,
    })


@login_required
def complete_payment(request):
    """Simulate payment completion."""
    if request.method != 'POST':
        return redirect('dashboard')

    booking_type   = request.POST.get('booking_type')
    booking_id     = request.POST.get('booking_id')
    payment_method = request.POST.get('payment_method', 'simulation')
    amount         = 0
    booking        = None

    try:
        if booking_type == 'vehicle':
            from vehicles.models import VehicleBooking
            booking = VehicleBooking.objects.get(booking_id=booking_id, tourist=request.user)
            amount  = booking.total_amount
            booking.status = 'confirmed'
            booking.save()

        elif booking_type == 'hotel':
            from hotels.models import HotelBooking
            booking = HotelBooking.objects.get(booking_id=booking_id, tourist=request.user)
            amount  = booking.total_amount
            booking.status = 'confirmed'
            booking.save()

        elif booking_type == 'guide':
            from guides.models import GuideBooking
            booking = GuideBooking.objects.get(booking_id=booking_id, tourist=request.user)
            amount  = booking.total_amount
            booking.status = 'confirmed'
            booking.save()

        tid = f"TXN{uuid.uuid4().hex[:12].upper()}"
        Payment.objects.create(
            user=request.user,
            transaction_id=tid,
            booking_type=booking_type,
            booking_id=booking_id,
            amount=amount,
            payment_method=payment_method,
            status='success',
            completed_at=timezone.now(),
        )
        Notification.objects.create(
            user=request.user, type='payment_success',
            title='Payment Successful!',
            message=f'₹{amount} paid for booking {booking_id}. Transaction: {tid}',
        )

        # Trigger email notifications to both tourist and service owner
        send_booking_emails(booking, booking_type)

        messages.success(request, f'✅ Payment successful! Booking {booking_id} confirmed. TXN: {tid}')
        return redirect('dashboard')

    except Exception as e:
        messages.error(request, f'Payment failed: {str(e)}')
        return redirect('dashboard')

