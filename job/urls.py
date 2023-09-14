from django.urls import path
from . import views

urlpatterns = [
    path("post", views.post_job, name='post_job'),
    path("jobs", views.view_jobs, name='view_job'),
    path("terms/<int:page>", views.job_pagination, name="terms-by-page"),
    path("details/<job_id>", views.job_details, name='job_detail'),
    path("apply/<job_id>", views.apply_job, name='apply_job'),
    path("apply/bid/<job_id>", views.bid_job, name='bid_job'),
    path("job/delete/<job_id>", views.delete_job, name='delete_job'),
    path("bid/request/<job_bid_id>/<notification_id>", views.view_bid, name='view_bid'),
    path("bid/reject/<job_bid_id>/<freelancer_id>", views.reject_bid, name='reject_bid'),
]