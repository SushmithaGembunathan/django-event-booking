from django.shortcuts import render, redirect
from .models import Event, Booking, LogEntry
from .forms import BookingForm
from django.contrib.auth.decorators import login_required

def event_list(request):
    events = Event.objects.all()
    return render(request, 'booking/event_list.html', {'events': events})

@login_required
def book_event(request, event_id):
    event = Event.objects.get(id=event_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.event = event
            if booking.seats_booked > event.seats_available:
                form.add_error('seats_booked', 'Not enough seats available.')
            else:
                booking.save()
                event.seats_available -= booking.seats_booked
                event.save()
                LogEntry.objects.create(
                    action_type='CREATE',
                    performed_by=request.user,
                    description=f"{request.user.username} booked {booking.seats_booked} seats for {event.name}"
                )
                return redirect('event_list')
    else:
        form = BookingForm()
    return render(request, 'booking/event_detail.html', {'event': event, 'form': form})
