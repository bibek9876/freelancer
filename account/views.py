import os
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from account.forms import (FreelancerRegistrationForm, 
                           UserLoginForm, 
                           AccountupdateForm, 
                           ImageUpdateForm, 
                           ClientRegistrationForm, 
                           CreateResume, 
                           AdminRegistrationForm, 
                           AdminLoginForm, 
                           AdminSaveAccount,)
from django.views.decorators.csrf import csrf_exempt
from account.models import Account, Resume, AdminDetails
from django_countries.fields import CountryField
from django.core.mail import send_mail
from django.contrib import messages
from uuid import uuid4
from django.urls import reverse
from account.decorators import admin_required
from django.http import JsonResponse
from job.models import JobApplies, JobBid, AgreedJob, JobSubCategories, JobCategories, Job
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from job.views import search_job

# Create your views here.

def admin_registration(request):
    context={}
    if request.POST:
        form=AdminSaveAccount(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            account = form.save(commit=False)
            # admin.password = set_password(password)
            account.save()
            form=AdminRegistrationForm(request.POST)
            if form.is_valid():
                ad = form.save(commit=False)
                rand_token = uuid4()
                ad.title="admin"
                ad.token=rand_token
                ad.save()
            
            
            
            # Sending email
            link = reverse('send_token', args=[str(rand_token)])
            subject = "Request for admin"
            message = f"Hello, {email} want to be registered as Admin. Use this link {link} to send token"
            email_from = email
            email_to=os.environ.get('EMAIL_HOST_USER')
            send_mail(subject,message,email_from,[email_to,])
            messages.success(request, 'Request for admin sent successfully')
            context['form'] = form
        else:
            messages.error(request,"There was an error sending the request")
    form = AdminRegistrationForm()
    context['form'] = form
    return render(request, 'admin/register.html', context)

def send_token(request, token):
    link = reverse('verify_token')
    admin_detail = AdminDetails.objects.get(token= token)
    subject = "Token for admin"
    message = f"Hello {admin_detail.first_name}, your token to be admin is {token}. Use this link {link} to enter token."
    email_from = os.environ.get('EMAIL_HOST_USER')
    email_to=admin_detail.email
    send_mail(subject,message,email_from,[email_to,])
    return redirect('admin_registration')

def verify_token(request):
    context={}
    if request.POST:
        form_token = request.POST['token']
        admin_detail = AdminDetails.objects.filter(token= form_token)
        if admin_detail.count() < 1:
            messages.error(request, "Token does not match.")
        else:
            admin_detail = AdminDetails.objects.get(token= form_token)
            account = Account.objects.get(email = admin_detail.email)
            admin_detail.status = "approved"
            admin_detail.save()
            account.is_admin = True
            account.save()
            messages.success(request, "Your admin request has been approved.")
            return redirect('admin_registration')
    return render(request, 'admin/enter_token.html', context)

@csrf_exempt
def login_ad(request):
    context={}
    
    if request.POST:
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email = email, password = password)
            login(request, user)
            return redirect('admin_dash')
                
    else:
        form = AdminLoginForm()
        
    context['login_form'] = form
    return render(request, 'admin/login_ad.html', context)

def ad_logout(request):
    logout(request)
    return redirect('login_ad')

@admin_required
def admin_dash(request):
    context={}
    return render(request, 'admin/dashboard.html', context)

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
                obj = form.save(commit=False)
                obj.user_type = user_type
                obj.save()
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
            return redirect('home')
                
    else:
        form = UserLoginForm()
        
    context['login_form'] = form
    return render(request, 'account/login.html', context)

def user_logout(request):
    logout(request)
    return redirect('home')

def search_jobs(request,
                page, 
                job_data,
               search_query="", 
               min_price="", 
               max_price="", 
               deadline="", 
               project_length="", 
               category="",
               ):
    
    context = {}
    jobs = job_data
    categories = JobSubCategories.objects.all()
    
    if search_query != "" and search_query is not None:
        jobs = jobs.filter(Q(job_title__icontains=search_query) | Q(description__icontains=search_query)).distinct()
    if min_price != "" and min_price is not None:
        query=min_price
        jobs = jobs.filter(rate__gte=query)
        
    if max_price != "" and max_price is not None:
        query=max_price
        jobs = jobs.filter(rate__lte=query)
    
    if deadline != "" and deadline is not None:
        query = deadline
        jobs = jobs.filter(
            completion_time__year= deadline.split('-')[0],
            completion_time__month= deadline.split('-')[1],
            completion_time__day= deadline.split('-')[2],
            )
    
    if project_length != "" and project_length is not None:
        query = project_length
        jobs = jobs.filter(
            project_length__icontains = query
        )
    
    if category != "" and category is not None:
        query = category
        jobs = jobs.filter(category__sub_category_name__contains = query)
    
    # paggination
    
    paginator = Paginator(jobs, 1)
    pagination_data = paginator.get_page(page)
    total_page = pagination_data.paginator.num_pages
    try:
        jobs = paginator.page(page)
    except PageNotAnInteger:
        jobs = paginator.page(1)
    except EmptyPage:
        jobs = paginator.page(paginator.num_pages)
    
    context['results'] = jobs
    context['categories'] = categories
    # context['query'] = query
    context['last_page'] = total_page
    context['pages'] = [n+1 for n in range(total_page)]
    # context['result_count'] = Job.objects.all().count()
    return render(request, 'home/search_result.html', context)


def dashboard(request):
    context = {}
    user_id = request.user.id
    job_bids = JobBid.objects.filter(freelancer_id = user_id)
    agreed_jobs = AgreedJob.objects.filter(freelancer_id = user_id)
    applied_jobs = JobApplies.objects.filter(freelancer_id = user_id)
    
    context["job_bid_count"] = job_bids.count()
    context["agreed_job_count"] = agreed_jobs.count()
    context["applied_job_count"] = applied_jobs.count()
    return render(request, 'account/freelancer_dashboard.html', context)

def agreed_jobs(request):
    context={}
    user_id = request.user.id
    job_data = JobBid.objects.raw(f'select j.*, aj.agreed_rate, aj.agreed_completion_time, aj.agreed_price_per from job_job j join job_agreedjob aj on j.id=aj.job_id where aj.freelancer_id = {user_id};')
    
    page=request.GET.get('page')
    paginator = Paginator(job_data, 5)
    pagination_data = paginator.get_page(page)
    total_page = pagination_data.paginator.num_pages
    try:
        job_data = paginator.page(page)
    except PageNotAnInteger:
        job_data = paginator.page(1)
    except EmptyPage:
        job_data = paginator.page(paginator.num_pages)
    context["agreed_jobs"] = job_data
    context['pages'] = [n+1 for n in range(total_page)]
    return render(request, 'account/freelancer_agreed_jobs.html', context)
    
def applied_jobs(request):
    context={}
    user_id = request.user.id
    job_data = JobBid.objects.raw(f'select j.*, aj.status from job_job j join job_jobapplies aj on j.id=aj.job_id where aj.freelancer_id = {user_id};')

    page=request.GET.get('page')
    paginator = Paginator(job_data, 5)
    pagination_data = paginator.get_page(page)
    total_page = pagination_data.paginator.num_pages
    try:
        job_data = paginator.page(page)
    except PageNotAnInteger:
        job_data = paginator.page(1)
    except EmptyPage:
        job_data = paginator.page(paginator.num_pages)
    context["agreed_jobs"] = job_data
    context['pages'] = [n+1 for n in range(total_page)]

    context["applied_jobs"] = job_data
    return render(request, 'account/freelancer_applied_jobs.html', context)
    
def job_bids(request):
    context={}
    user_id = request.user.id
    job_data = JobBid.objects.raw(f'select j.*, aj.rate, aj.completion_time, aj.price_per from job_job j join job_jobbid aj on j.id=aj.job_id where aj.freelancer_id = {user_id};')

    page=request.GET.get('page')
    paginator = Paginator(job_data, 5)
    pagination_data = paginator.get_page(page)
    total_page = pagination_data.paginator.num_pages
    try:
        job_data = paginator.page(page)
    except PageNotAnInteger:
        job_data = paginator.page(1)
    except EmptyPage:
        job_data = paginator.page(paginator.num_pages)
    context["agreed_jobs"] = job_data
    context['pages'] = [n+1 for n in range(total_page)]

    context["job_bids"] = job_data
    return render(request, 'account/freelancer_job_bids.html', context)

def view_user(request, user_id):
    context = {}
    user = request.user
    if user.is_authenticated:
        resume = Resume.objects.filter(freelancer_id = user_id).first
        resume_count = Resume.objects.filter(freelancer_id = user_id).count()
        user_profile = Account.objects.get(id = user_id)
    context['user_profile'] = user_profile
    context['resume'] = resume
    context['resume_count'] = resume_count
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
