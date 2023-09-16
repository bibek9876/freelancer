from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_page, name='home'),
    path("job/search/", views.search_job, name='search_job'),
    path("contact/", views.contact, name='contact'),
    path("freelancers/", views.freelancer_list, name='freelancer_list'),
    # path("filter_jobs", views.filter_jobs, name='filter_jobs'),
]