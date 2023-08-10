from django.contrib import admin
from account.models import Account
from job.models import Job
# Register your models here.

admin.site.register(Account)
admin.site.register(Job)