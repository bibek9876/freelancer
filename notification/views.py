from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notification, Account
from django.db import connection, transaction

# Create your views here.

@login_required
def notification(request, id):
    context = {}
    notifications = Notification.objects.filter(receiver_id=request.user.id).order_by("-id")
    # freelancer_details = Account.objects.filter(id = notifications.sender_id)
    # cursor = connection.cursor()
    # cursor.execute("select a.* from account_account a join notification_notification n on n.sender_id = a.id;")
    freelancer = Account.objects.raw(f'select a.*, n.link, n.message, n.id as "notification_id" from account_account a join notification_notification n on n.sender_id = a.id where n.receiver_id = {request.user.id};')
    # freelancer = Notification.objects.filter(sender_id=id).select_related() 
    context['notifications'] = notifications
    context['freelancer'] = freelancer
    return render(request, 'notification/notification.html', context)