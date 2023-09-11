import os
import pdb
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from account.forms import FreelancerRegistrationForm, UserLoginForm, AccountupdateForm, ImageUpdateForm, ClientRegistrationForm, CreateResume
from django.views.decorators.csrf import csrf_exempt
from account.models import Account, Resume
from django_countries.fields import CountryField

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
        if request.POST:
            form = ClientRegistrationForm(request.POST)
            if form.is_valid():
                email = request.POST['email']
                username = request.POST['username']
                first_name = request.POST['first_name']
                last_name = request.POST['last_name']
                password = request.POST['password1']
                
                obj = form.save(commit=False)
                obj.first_name = first_name
                obj.last_name = last_name
                obj.username = username
                obj.email = email
                obj.user_type = user_type
                obj.save()
                account = authenticate(email = email, password = password)
                login(request, account)
                return redirect('home')
            else:
                context['form'] = form
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
    
    if request.POST:
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            
            user = authenticate(email = email, password = password)
            login(request, user)
            
                
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
        resume = Resume.objects.filter(freelancer_id = user_id).first
        user_profile = Account.objects.get(id = user_id)
        # pdb.set_trace()
    context['user_profile'] = user_profile
    context['resume'] = resume
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
    resume = Resume.objects.filter(freelancer_id = user_id)
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
    context["resume_count"] = resume.count()
    context["resume"] = resume
    return render(request, 'account/update_profile.html', context)

@csrf_exempt
def build_resume(request, user_id):
    context ={}
    user = Account.objects.get(id=user_id)
    form = CreateResume(request.POST)
    if request.POST:
        if form.is_valid():
            obj = form.save(commit=False)
            obj.freelancer_id = user_id
            obj.skills = []
            obj.languages = []
            for skill in request.POST.getlist('skills'):
                obj.skills.append(skill.capitalize())
            for language in request.POST.getlist('languages'):
                obj.languages.append(language.capitalize())
            obj.save()
            return redirect('view_user', user_id)
        else:
            context['form'] = form
        context['user'] = user
    return render(request, 'account/build_resume.html', context)