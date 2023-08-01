from django.urls import path
from . import views

urlpatterns = [
    path("post", views.post_job, name='post_job'),
    path("view_job", views.view_jobs, name='view_job'),
]