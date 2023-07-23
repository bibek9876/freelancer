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