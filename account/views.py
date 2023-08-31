import os
import pdb
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from account.forms import FreelancerRegistrationForm, UserLoginForm, AccountupdateForm, ImageUpdateForm
from django.views.decorators.csrf import csrf_exempt
from account.models import Account
# Create your views here.


def type_selection(request):
    context = {}
    if request.GET:
        user_type = request.GET['user_type']
        return redirect('user_registration', user_type)
    return render(request, 'account/type_selection.html', context)

@csrf_exempt
def user_registration(request, user_type):
    context = {}
    if user_type == "client":
        return render(request, 'account/client_register.html', context)
    else:
        if request.POST:
            form = FreelancerRegistrationForm(request.POST)
            if form.is_valid():
                form.save()
                email = form.cleaned_data.get('email')
                raw_password = form.cleaned_data.get('password1')
                account = authenticate(email = email, password = raw_password)
                login(request, account)
                return redirect('home')
            else:
                context['registration_form'] = form
        else:
            form = FreelancerRegistrationForm()
            context['registration_form'] = form
        return render(request, 'account/freelancer_register.html', context)

@csrf_exempt
def user_login(request):
    context = {}
    
    user = request.user
    if user.is_authenticated:
        return redirect('home')
    
    if request.POST:
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            
            user = authenticate(email = email, password = password)
            
            if user:
                login(request, user)
                return redirect('home')
    else:
        form = UserLoginForm()
        
    context['login_form'] = form
    return render(request, 'account/login.html', context)

def user_logout(request):
    logout(request)
    return redirect('home')

def view_user(request, user_id):
    context = {}
    user = request.user
    if user.is_authenticated:
        user_profile = Account.objects.get(id = user_id)
    context['user_profile'] = user_profile
    return render(request, 'account/view_profile.html', context)

def update_profile_image(request, user_id):
    context = {}
    user = Account.objects.get(id=user_id)
    context['user'] = user
    if request.POST:
        form = ImageUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            if user.profile_image:
                image_path = user.profile_image.path
                if os.path.exists(image_path):
                    os.remove(image_path)
                form.save()
            else:
                form.save()
                return redirect('view_user', user_id)
        else:
            form = ImageUpdateForm()
            context['form'] = form
    return render(request, 'account/update_image.html')

def update_profile(request, user_id):
    context = {}
    user = Account.objects.get(id=user_id)
    if request.POST:
        if request.POST['country'] == "":
            country = user.country.code
        else:
            country = request.POST['country']
        form = AccountupdateForm(request.POST, instance=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            
            obj.country = country
            obj.save()
            context["success_message"] = "Updated Succcessfully"
            form = AccountupdateForm()
            return redirect('view_user', user_id)
        else:
            context['form'] = form
    else:
        form = AccountupdateForm()
        context['form'] = form
    context["user"] = user
    return render(request, 'account/update_profile.html', context)