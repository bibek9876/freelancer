from django.db import models
from account.models import Account
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django_resized import ResizedImageField
import datetime
import pathlib

# Create your models here.
def upload_location(instance, filename):
    file_path = 'job/{job_id}/-{filename}'.format(
        job_id=str(instance.user.id), filename= str(datetime.datetime.now().timestamp()) + pathlib.Path(filename).suffix
    )
    return file_path
    
class Job(models.Model):
    user = models.ForeignKey(Account, verbose_name = "user id", on_delete = models.CASCADE)
    task_type = models.CharField(max_length=50, null=False, default="IT")
    image = ResizedImageField(upload_to=upload_location, null=True, blank=True)
    job_title = models.CharField(max_length=200)
    rate = models.IntegerField()
    hour = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(max_length=600)
    completion_time = models.CharField(max_length=50)
    
    
@receiver(post_delete, sender=Job)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)
    
# def pre_save_receiver(sender, instance, *args, **kwargs):
#     if not instance.unique_field:
#         instance.unique_field = slugify(instance.user.username + "-" + datetime.datetime.now().timestamp)
        
# pre_save.connect(pre_save_receiver, sender=Job)
    
class JobBid(models.Model):
    freelancer = models.ForeignKey(Account, null = True, related_name='freelancer', on_delete = models.CASCADE)
    client = models.ForeignKey(Account, null = True, related_name='client', on_delete = models.CASCADE)
    requested_rate = models.IntegerField()
    requested_hour = models.DecimalField(max_digits=5, decimal_places=2)
    requested_completion_time = models.CharField(max_length=50)
    
class AggerdJob(models.Model):
    freelancer = models.ForeignKey(Account, null = True, related_name='worker', on_delete = models.CASCADE)
    client = models.ForeignKey(Account, null = True, related_name='employer', on_delete = models.CASCADE)
    agreed_rate = models.IntegerField()
    agreed_hour = models.DecimalField(max_digits=5, decimal_places=2)
    agreed_completion_time = models.CharField(max_length=50)
    