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

class Job(models.Model):
    user = models.ForeignKey(Account, verbose_name = "user id", on_delete = models.CASCADE)
    task_type = models.CharField(max_length=50, null=False, default="IT")
    image = ResizedImageField(upload_to=upload_location, null=True, blank=True)
    job_title = models.CharField(max_length=200)
    price_per = models.CharField(max_length=200)
    project_length = models.CharField(max_length=200)
    rate = models.IntegerField()
    description = models.TextField(max_length=600)
    completion_time = models.DateField()
    job_status = models.CharField(max_length=50, default="not assigned")
    category = models.ForeignKey(JobSubCategories, verbose_name = "job_sub_category", on_delete = models.CASCADE)
    freelancer_experience = models.CharField(max_length=50, null=False)
    created_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    
@receiver(post_delete, sender=Job)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)
    
    
class JobBid(models.Model):
    freelancer = models.ForeignKey(Account, null = True, related_name='freelancer', on_delete = models.CASCADE)
    client = models.ForeignKey(Account, null = True, related_name='client', on_delete = models.CASCADE)
    job = models.ForeignKey(Job, null = True, related_name='jobbid', on_delete = models.CASCADE)
    rate = models.IntegerField()
    price_per = models.CharField(max_length=50)
    completion_time = models.DateField()
    status = models.CharField(max_length=50, default="not reviewed")
    created_at = models.DateField(auto_now_add=True, blank=False, null=False)

class JobApplies(models.Model):
    freelancer = models.ForeignKey(Account, null = True, related_name='job_apply_freelancer', on_delete = models.CASCADE)
    client = models.ForeignKey(Account, null = True, related_name='job_apply_client', on_delete = models.CASCADE)
    job = models.ForeignKey(Job, null = True, related_name='job_apply', on_delete = models.CASCADE)
    status = models.CharField(max_length=50, default="requested")
    created_at = models.DateField(auto_now_add=True, blank=False, null=False)
    
class AgreedJob(models.Model):
    freelancer = models.ForeignKey(Account, null = True, related_name='worker', on_delete = models.CASCADE)
    client = models.ForeignKey(Account, null = True, related_name='employer', on_delete = models.CASCADE)
    job = models.ForeignKey(Job, null = True, related_name='job', on_delete = models.CASCADE)
    agreed_rate = models.IntegerField()
    agreed_price_per = models.CharField(max_length=50)
    agreed_completion_time = models.CharField(max_length=50)
    created_at = models.DateField(auto_now_add=True, blank=False, null=False)
    
class RejectionReason(models.Model):
    reason = models.CharField(max_length=500, null=False, blank=False)
    reject_option = models.CharField(max_length=500, null=False, blank=False)
    freelancer = models.ForeignKey(Account, null = True, related_name='freelancer1', on_delete = models.CASCADE)
    client = models.ForeignKey(Account, null = True, related_name='client1', on_delete = models.CASCADE)
    job = models.ForeignKey(Job, null=False, related_name="job1", on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True, blank=False, null=False)

@receiver(post_delete, sender=JobCategories)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)



class Contact(models.Model):
    name=models.CharField(max_length=100, blank=False, null=False)
    phone=PhoneNumberField(blank=True)
    email=models.EmailField(unique=False)
    message=models.TextField()
    created_at = models.DateField(auto_now_add=True, blank=False, null=True)
    
    
class UserPayment(models.Model):
    job_agreed = models.ForeignKey(AgreedJob, on_delete=models.CASCADE)
    payment_bool = models.BooleanField(default=False)
    stripe_checkout_id = models.CharField(max_length=500)
    created_at = models.DateField(auto_now_add=True)