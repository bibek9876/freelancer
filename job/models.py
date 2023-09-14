import pdb
from django.db import models
from account.models import Account
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django_resized import ResizedImageField
import datetime
import pathlib
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
def upload_location(instance, filename):
    file_path = 'job/{job_id}/-{filename}'.format(
        job_id=str(instance.user.id), filename= str(datetime.datetime.now().timestamp()) + pathlib.Path(filename).suffix
    )
    return file_path

def category_upload_location(instance, filename):
    #Creating new id for naming of a folder
    if not instance.id:
        Model = instance.__class__
        new_id=None
        try:
            new_id = Model.objects.order_by("id").last().id
            if new_id:
                new_id += 1
            else:
                pass
        except:
            new_id=1
    else:
        new_id = instance.id
    #getting a file path
    file_path = 'category/{category_id}/-{filename}'.format(
        category_id=str(new_id), filename= str(datetime.datetime.now().timestamp()) + pathlib.Path(filename).suffix
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
    job_status = models.CharField(max_length=50, default="not assigned")
    created_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    
@receiver(post_delete, sender=Job)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)
    
    
class JobBid(models.Model):
    freelancer = models.ForeignKey(Account, null = True, related_name='freelancer', on_delete = models.CASCADE)
    client = models.ForeignKey(Account, null = True, related_name='client', on_delete = models.CASCADE)
    job = models.ForeignKey(Job, null = True, related_name='jobbid', on_delete = models.CASCADE)
    requested_rate = models.IntegerField()
    requested_hour = models.DecimalField(max_digits=5, decimal_places=2)
    requested_completion_time = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default="not reviewed")
    
class AgreedJob(models.Model):
    freelancer = models.ForeignKey(Account, null = True, related_name='worker', on_delete = models.CASCADE)
    client = models.ForeignKey(Account, null = True, related_name='employer', on_delete = models.CASCADE)
    job = models.ForeignKey(Job, null = True, related_name='job', on_delete = models.CASCADE)
    agreed_rate = models.IntegerField()
    agreed_hour = models.DecimalField(max_digits=5, decimal_places=2)
    agreed_completion_time = models.CharField(max_length=50)
    
class RejectionReason(models.Model):
    reason = models.CharField(max_length=500, null=False, blank=False)
    freelancer = models.ForeignKey(Account, null = True, related_name='freelancer1', on_delete = models.CASCADE)
    client = models.ForeignKey(Account, null = True, related_name='client1', on_delete = models.CASCADE)
    job = models.ForeignKey(Job, null=False, related_name="job1", on_delete=models.CASCADE)
    

class JobCategories(models.Model):
    category_name = models.CharField(max_length=30, blank=False, null=False)
    image =  ResizedImageField(upload_to=category_upload_location, null=True, blank=True)
    slug = models.SlugField()
    description = models.CharField(max_length=500, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.category_name}"


class JobSubCategories(models.Model):
    job_categories = models.ForeignKey(JobCategories, null = True, related_name='job_categories', on_delete = models.CASCADE)
    sub_category_name = models.CharField(max_length=50, blank=False, null=False)
    image =  ResizedImageField(upload_to=category_upload_location, null=True, blank=True)
    description = models.CharField(max_length=500, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sub_category_name}"

@receiver(post_delete, sender=JobCategories)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)



class Contact(models.Model):
    name=models.CharField(max_length=100, blank=False, null=False)
    phone=PhoneNumberField(blank=True)
    email=models.EmailField(unique=False)
    message=models.TextField()