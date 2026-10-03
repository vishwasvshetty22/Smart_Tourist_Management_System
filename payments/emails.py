import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


def format_dt(dt):
    """Safely format datetime and date objects to readable strings."""
    if hasattr(dt, 'strftime'):
        try:
            return dt.strftime('%d-%b-%Y %I:%M %p')
        except ValueError:
            # It's a date object (no %I or %M)
            return dt.strftime('%d-%b-%Y')
    return str(dt)


def send_booking_emails(booking, booking_type):
    """Sends notification emails to both the Tourist and the respective Service Owner/Provider."""
    try:
        tourist_email = booking.tourist.email
        tourist_name = booking.tourist.get_full_name() or booking.tourist.username
        booking_id = booking.booking_id
        amount = booking.total_amount
        
        # Determine owner, owner_email, item_name, and details
        if booking_type == 'vehicle':
            owner = booking.vehicle.owner
            owner_email = owner.email
            owner_name = owner.get_full_name() or owner.username
            item_name = f"{booking.vehicle.brand} {booking.vehicle.model} ({booking.vehicle.get_vehicle_type_display()})"
            details = (
                f"Rental Type: {booking.get_rental_type_display()}\n"
                f"Pickup Location: {booking.pickup_location}\n"
                f"Duration: {format_dt(booking.start_datetime)} to {format_dt(booking.end_datetime)}"
            )
        elif booking_type == 'hotel':
            owner = booking.hotel.owner
            owner_email = owner.email
            owner_name = owner.get_full_name() or owner.username
            item_name = f"{booking.hotel.name} - {booking.room.get_room_type_display()} Room (Room {booking.room.room_number})"
            details = (
                f"Guests: {booking.guests_count}\n"
                f"Check-in: {format_dt(booking.check_in_date)}\n"
                f"Check-out: {format_dt(booking.check_out_date)}\n"
                f"Nights: {booking.nights}"
            )
        elif booking_type == 'guide':
            owner = booking.guide.user
            owner_email = owner.email
            owner_name = owner.get_full_name() or owner.username
            item_name = f"Tour Guide Service by {booking.guide.name}"
            details = (
                f"Location: {booking.location.name if booking.location else 'Not Specified'}\n"
                f"Meeting Point: {booking.meeting_point}\n"
                f"Group Size: {booking.group_size}\n"
                f"Duration: {format_dt(booking.start_datetime)} to {format_dt(booking.end_datetime)}"
            )
        else:
            return

        # 1. Send Email to Tourist
        tourist_subject = f"Booking Confirmation - ID: {booking_id} [{booking_type.capitalize()}]"
        tourist_body = f"""Dear {tourist_name},

Thank you for using Smart Tourist! Your payment has been successfully processed, and your booking is now CONFIRMED.

Booking Summary:
------------------------------------------
Booking ID:   {booking_id}
Service Type: {booking_type.capitalize()}
Name:         {item_name}
Total Paid:   ₹{amount}
Details:
{details}
------------------------------------------

If you have any questions, please contact the service provider or reach out to our admin support.

Happy travels,
The Smart Tourist Team"""

        send_mail(
            subject=tourist_subject,
            message=tourist_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[tourist_email],
            fail_silently=False,
        )
        logger.info(f"Booking confirmation email sent to Tourist: {tourist_email}")

        # 2. Send Email to Owner/Provider
        owner_subject = f"New Confirmed Booking Received - ID: {booking_id}"
        owner_body = f"""Dear {owner_name},

Great news! A new booking has been confirmed for your service on the Smart Tourist Platform.

Booking Details:
------------------------------------------
Booking ID:    {booking_id}
Customer:      {tourist_name} ({tourist_email})
Service/Item:  {item_name}
Total Paid:    ₹{amount}
Details:
{details}
------------------------------------------

Please log in to your dashboard to review this booking and prepare for the customer.

Best regards,
The Smart Tourist Team"""

        send_mail(
            subject=owner_subject,
            message=owner_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[owner_email],
            fail_silently=False,
        )
        logger.info(f"New booking alert email sent to Owner: {owner_email}")

    except Exception as e:
        logger.error(f"Error sending booking/payment email notifications: {e}")


def send_cancellation_emails(booking, booking_type, reason=""):
    """Sends cancellation notification emails to both the Tourist and the respective Service Owner/Provider."""
    try:
        tourist_email = booking.tourist.email
        tourist_name = booking.tourist.get_full_name() or booking.tourist.username
        booking_id = booking.booking_id
        
        # Determine owner, owner_email, item_name
        if booking_type == 'vehicle':
            owner = booking.vehicle.owner
            owner_email = owner.email
            owner_name = owner.get_full_name() or owner.username
            item_name = f"{booking.vehicle.brand} {booking.vehicle.model}"
        elif booking_type == 'hotel':
            owner = booking.hotel.owner
            owner_email = owner.email
            owner_name = owner.get_full_name() or owner.username
            item_name = f"{booking.hotel.name} - Room {booking.room.room_number}"
        elif booking_type == 'guide':
            owner = booking.guide.user
            owner_email = owner.email
            owner_name = owner.get_full_name() or owner.username
            item_name = f"Tour Guide Service by {booking.guide.name}"
        else:
            return

        reason_str = f"\nReason for Cancellation: {reason}" if reason else ""

        # 1. Send Email to Tourist
        tourist_subject = f"Booking Cancelled - ID: {booking_id} [{booking_type.capitalize()}]"
        tourist_body = f"""Dear {tourist_name},

This email confirms that your booking has been CANCELLED.

Cancellation Details:
------------------------------------------
Booking ID:   {booking_id}
Service Type: {booking_type.capitalize()}
Name:         {item_name}{reason_str}
------------------------------------------

If you made a payment, any refund will be processed according to our cancellation policies.

Best regards,
The Smart Tourist Team"""

        send_mail(
            subject=tourist_subject,
            message=tourist_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[tourist_email],
            fail_silently=False,
        )
        logger.info(f"Cancellation email sent to Tourist: {tourist_email}")

        # 2. Send Email to Owner/Provider
        owner_subject = f"Booking Cancelled by Customer - ID: {booking_id}"
        owner_body = f"""Dear {owner_name},

This email is to notify you that the booking {booking_id} for your service has been CANCELLED by the customer.

Cancellation Details:
------------------------------------------
Booking ID:    {booking_id}
Customer:      {tourist_name} ({tourist_email})
Service/Item:  {item_name}{reason_str}
------------------------------------------

The reservation dates/slots have been released and are now available for other users.

Best regards,
The Smart Tourist Team"""

        send_mail(
            subject=owner_subject,
            message=owner_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[owner_email],
            fail_silently=False,
        )
        logger.info(f"Cancellation alert email sent to Owner: {owner_email}")

    except Exception as e:
        logger.error(f"Error sending cancellation email notifications: {e}")
