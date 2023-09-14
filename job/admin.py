from django.contrib import admin
from job.models import JobCategories, JobSubCategories
# Register your models here.


admin.site.register(JobCategories)
admin.site.register(JobSubCategories)