from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_page, name='home'),
    path("job/search/", views.search_job, name='search_job'),
]