from django.db import models
from account.models import Account

# Create your models here.


class Job(models.Model):
    user = models.ForeignKey(Account, verbose_name = "user id", on_delete = models.CASCADE)
    job_title = models.CharField(max_length=200)
    rate = models.IntegerField()
    hour = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(max_length=600)
    completion_time = models.CharField(max_length=50)
    
class JobBid(models.Model):
    freelancer = models.ForeignKey(Account, null = True, related_name='freelancer', on_delete = models.CASCADE)
    client = models.ForeignKey(Account, null = True, related_name='client', on_delete = models.CASCADE)
    requested_rate = models.IntegerField()
    requested_hour = models.DecimalField(max_digits=5, decimal_places=2)
    requested_completion_time = models.CharField(max_length=50)