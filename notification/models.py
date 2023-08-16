from django.db import models
from account.models import Account
from django.urls import reverse

# Create your models here.

class Notification(models.Model):
    receiver = models.ForeignKey(Account,related_name='receiver', on_delete=models.CASCADE)
    sender = models.ForeignKey(Account,related_name='sender', on_delete=models.CASCADE)
    message = models.TextField()
    link = models.URLField(blank=True, null=True)
    read = models.BooleanField(default=False)