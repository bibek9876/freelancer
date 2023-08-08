from django.urls import path
from . import views

urlpatterns = [
    path("post", views.post_job, name='post_job'),
    path("jobs", views.view_jobs, name='view_job'),
    path("details/<job_id>", views.job_details, name='job_detail'),
    path("apply/<job_id>", views.apply_job, name='apply_job'),
    path("apply/bid/<job_id>", views.bid_job, name='bid_job'),
]