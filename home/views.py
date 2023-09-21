import os
import pdb
from django.shortcuts import render, redirect
from job.models import Job, JobSubCategories
from account.models import Account
from home.forms import ContactForm
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.contrib import messages
from django.db.models import Q

from django.contrib.postgres.search import SearchVector
from home.decorators import resume_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.

def home_page(request):
    context = {}
    user = request.user
    freelancers = Account.objects.filter(user_type = 'freelancer')
    job_list = Job.objects.filter(job_status="not assigned")
    if user.is_authenticated:
        user_type = user.user_type
        context['user_type'] = user_type
    context["job_list"] = job_list
    context["freelancers"] = freelancers
    return render(request, 'home/home.html', context)

@csrf_exempt
def search_job(request):
    context = {}
    jobs = Job.objects.all()
    pdb.set_trace()
    categories = JobSubCategories.objects.all()
    query = request.GET.get('query')
    if request.GET.get('query') != "" and request.GET.get('query') is not None:
        query = request.GET.get('query')
        jobs = jobs.filter(Q(job_title__icontains=query) | Q(description__icontains=query)).distinct()
    if request.GET.get('min_price') != "" and request.GET.get('min_price') is not None:
        query=request.GET.get('min_price')
        jobs = jobs.filter(rate__gte=query)
        
    if request.GET.get('max_price') != "" and request.GET.get('max_price') is not None:
        query=request.GET.get('max_price')
        jobs = jobs.filter(rate__lte=query)
    
    if request.GET.get('deadline') != "" and request.GET.get('deadline') is not None:
        query = request.GET.get('deadline')
        jobs = jobs.filter(
            completion_time__year= request.GET.get('deadline').split('-')[0],
            completion_time__month= request.GET.get('deadline').split('-')[1],
            completion_time__day= request.GET.get('deadline').split('-')[2],
            )
    
    if request.GET.get('project_length') != "" and request.GET.get('project_length') is not None:
        query = request.GET.get('project_length')
        jobs = jobs.filter(
            project_length__icontains = query
        )
    
    if request.GET.get('category') != "" and request.GET.get('category') is not None:
        query = request.GET.get('category')
        jobs = jobs.filter(category__sub_category_name__contains = query)
    pdb.set_trace()
    
    # paggination
    page = request.GET.get("page")
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
    context['query'] = query
    context['last_page'] = total_page
    context['pages'] = [n+1 for n in range(total_page)]
    # context['result_count'] = Job.objects.all().count()
    return render(request, 'home/search_result.html', context)

# @csrf_exempt
# def filter_jobs(request):
#     context = {}
#     sort_by_price=request.POST['sort_price']
#     if sort_by_price == "low_to_high":
#         result = Job.objects.order_by("rate")
#     elif sort_by_price == "high_to_low":
#         result = Job.objects.order_by("-rate")
#     context['results'] = result
#     return render(request, 'home/search_result.html', context)

def freelancer_list(request):
    context = {}
    freelancer = Account.objects.all().filter(user_type="freelancer")
    paginator = Paginator(freelancer, 6)
    page_number = request.GET.get('page')
    pagination_data = paginator.get_page(page_number)
    total_page = pagination_data.paginator.num_pages
    context['freelancer'] = pagination_data
    context['last_page'] = total_page
    context['pages'] = [n+1 for n in range(total_page)]
    return render(request, 'home/freelancer_lists.html', context)

def freelancer_search(request):
    context={}
    freelancers = Account.objects.all()
    
    if request.GET.get("freelancer") != "" and request.GET.get("freelancer") is not None:
        query = request.GET.get('freelancer')
        freelancer = freelancers.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query)).distinct()
    
    paginator = Paginator(freelancer, 6)
    page_number = request.GET.get('page')
    pagination_data = paginator.get_page(page_number)
    total_page = pagination_data.paginator.num_pages
    context['freelancer'] = pagination_data
    context['last_page'] = total_page
    context['pages'] = [n+1 for n in range(total_page)]
    return render(request, 'home/freelancer_lists.html', context)


@csrf_exempt
def contact(request):
    context={}
    if request.POST:
        form=ContactForm(request.POST)
        if form.is_valid():
            form.save()
            context['form'] = form
            
            # notification
            subject = "Feedback for web portal"
            message = request.POST['message']
            email_from = request.POST['email']
            email_to=os.environ.get('EMAIL_HOST_USER')
            send_mail(subject,message,email_from,[email_to,])
            # messages.success(request, 'Request for admin sent successfully')
            return redirect('contact')
        context['form'] = form
    else:
        form=ContactForm()
        context['form'] = form
    return render(request, 'home/contact.html', context)