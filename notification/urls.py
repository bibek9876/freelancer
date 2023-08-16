from django.urls import path
from . import views

urlpatterns = [
    path("notification/<id>", views.notification, name='notification'),
]