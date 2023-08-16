from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notification

# Create your views here.

@login_required
def notification(request, id):
    context = {}
    notifications = Notification.objects.filter(receiver_id=id).order_by("-id")
    context['notifications'] = notifications
    return render(request, 'notification/notification.html', context)