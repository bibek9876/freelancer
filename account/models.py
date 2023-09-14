import pathlib
from tkinter import Image
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.postgres.fields import ArrayField
from django_countries.fields import CountryField
from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_save
from django.utils.text import slugify
import datetime
from django_resized import ResizedImageField

# Create your models here.

def upload_location(instance, filename):
    file_path = 'account/{userid}/profile/-{filename}'.format(
        userid = str(instance.id), filename=str(datetime.datetime.now().timestamp()) + pathlib.Path(filename).suffix
    )
    return file_path

class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("Please enter email address.")
        if not username:
            raise ValueError("Please enter username")
        
        user = self.model(
            email = self.normalize_email(email),
            username = username,
        )
        user.set_password(password)
        user.save(using = self._db)
        return user
    
    def create_superuser(self, username, email, password):
        user = self.create_user(
            email = self.normalize_email(email),
            password=password,
            username=username,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        
        user.save(using=self._db)
        return user

class Account(AbstractBaseUser):
    first_name = models.CharField(verbose_name='First Name', max_length=30, blank=False)
    last_name = models.CharField(verbose_name='Last Name', max_length=30, blank=False)
    profile_image = ResizedImageField(upload_to=upload_location, null=True, blank = True)
    title = models.CharField(verbose_name='Title', max_length=30, blank=True, null=True)
    phone_number = PhoneNumberField(blank=True)
    country = CountryField()
    email = models.EmailField(verbose_name="Email", max_length=254, unique=True)
    username = models.CharField(verbose_name="Username", max_length=30, unique=True)
    user_type = models.CharField(verbose_name="User type", max_length=30, blank=True, default="guest")
    sign_in_mode = models.CharField(max_length=30, blank=True, default="normal")
    last_login = models.DateTimeField(verbose_name="Last login", auto_now=True)
    date_joined = models.DateTimeField(verbose_name="Date joined", auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)



    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username'
    ]
    
    objects = MyAccountManager()
    
    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
    
@receiver(post_delete, sender=Account)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)
    
# def pre_save_receiver(sender, instance, *args, **kwargs):
#     if not instance.username:
#         instance.username = slugify(instance.user.username + "-" + datetime.datetime.now().timestamp)
        
# pre_save.connect(pre_save_receiver, sender=Account)

class AdminDetails(models.Model):
    first_name=models.CharField(max_length=50, null=False)
    last_name=models.CharField(max_length=50, null=False)
    email=models.EmailField(max_length=200, null=False)
    status=models.CharField(max_length=200, null=False, default="waiting")
    token=models.CharField(max_length=200, null=False, default="token")
    joined_date=models.DateTimeField(verbose_name="Date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="Last login", auto_now=True)
    
class Freelancerdetails(models.Model):
    user = models.ForeignKey(Account, null = True, related_name='freelancer_details', on_delete = models.CASCADE)
    hourly_rate = models.DecimalField(max_digits=3, decimal_places=2)
    state = models.CharField(max_length=20)
    zip = models.IntegerField()
    street_address = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    country = CountryField()
    
class ClientDetails(models.Model):
    user = models.ForeignKey(Account, null = True, related_name='client_details', on_delete = models.CASCADE)
    state = models.CharField(max_length=20)
    zip = models.IntegerField()
    street_address = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    country = CountryField()

class Business(models.Model):
    client = models.ForeignKey(ClientDetails, null=True, related_name="client_business", on_delete=models.CASCADE)
    business_name = models.CharField(max_length=100)
    state = models.CharField(max_length=20)
    zip = models.IntegerField()
    street_address = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    country = CountryField()

class Resume(models.Model):
    freelancer = models.ForeignKey(Account, null = True, related_name='freelancer_resume', on_delete = models.CASCADE)
    title = models.CharField(max_length=100)
    bio = models.TextField()
    languages = ArrayField(
                        models.CharField(max_length=200, blank=True),
                        size=8,
                    )
    skills = ArrayField(
                        models.CharField(max_length=200, blank=True),
                        size=8,
                    )

class Experience(models.Model):
    resume = models.ForeignKey(Resume, null = True, related_name='resume_experience', on_delete = models.CASCADE)
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    city = models.CharField(max_length= 50)
    country = CountryField()
    currently_working = models.BooleanField()
    start_date = models.DateField()
    end_date = models.DateField()

class Education(models.CharField):
    resume = models.ForeignKey(Resume, null = True, related_name='resume_education', on_delete = models.CASCADE)
    school_name = models.CharField(max_length=100)
    degree = models.CharField(max_length=100)
    field = models.CharField(max_length=100)
    start_date = models.CharField(max_length=100)
    end_date = models.CharField(max_length=100)
    description = models.TextField()