from django.urls import path
from . import views
from job.views import must_authenticate

urlpatterns = [
    path("register/", views.user_registration, name='register'),
    path("mustauthenticate/", must_authenticate, name='must_authenticate'),
    path("login/", views.user_login, name='login'),
    path("logout/", views.user_logout, name='logout'),
    path("user/profile/<user_id>", views.view_user, name='view_user'),
    path("user/profile/update/<user_id>", views.update_profile, name='update_profile'),
]