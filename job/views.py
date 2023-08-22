from django.shortcuts import render, redirect, get_object_or_404
from job.forms import PostJob, RequestBid, AcceptBid
from job.models import Job, JobBid, AgreedJob
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from account.models import Account
from notification.models import Notification
from django.urls import reverse
from django.contrib.auth.decorators import login_required
# Create your views here.

def must_authenticate(request):
    context = {}
    return render(request, 'account/must_authenticate.html', context)


@csrf_exempt
def post_job(request):
    context= {}
    user = request.user
    if not user.is_authenticated:
        return redirect('must_authenticate')
    else:
        user_id = user.id
        context['user'] = user_id
        if request.POST:
            form = PostJob(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                # user = user_id
                # obj.save()
                # form = PostJob()
                return redirect('home')
            else:
                context['post_job'] = form
        else:
            form = PostJob()
            context['post_job'] = form
        return render(request, 'job/post_job.html', context)

def view_jobs(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        if user.user_type == "client":
            jobs = Job.objects.filter(user_id=user.id)
        else:
            jobs = Job.objects.all()
    else:
        jobs = Job.objects.all()
    context['jobs'] = jobs
    return render(request, 'job/view_jobs.html', context)

def job_details(request, job_id):
    context = {}
    try:
        job_detail = Job.objects.get(pk=job_id)
    except Job.DoesNotExist:
        raise Http404("No job matches the given query.")
    context["job"] = job_detail
    return render(request, 'job/job_details.html', context)

@login_required
@csrf_exempt
def apply_job(request, job_id):
    context = {}
    try:
        job_detail = Job.objects.get(pk=job_id)
    except Job.DoesNotExist:
        raise Http404("No job matches the given query.")
    context["job"] = job_detail
    
    get_job = Job.objects.get(id = job_id)
    form = PostJob(request.POST)
    if form.is_valid():
        get_job.rate = request.POST['rate']
        get_job.hour = request.POST['hour']
        get_job.completion_time = request.POST['completion_time']
        get_job.save()
    else:
        form = PostJob()
        context["post_job_form"] = form
        
    return render(request, 'job/apply_jobs.html', context)
@login_required
@csrf_exempt
def bid_job(request, job_id):
    context={}
    job = Job.objects.get(id = job_id)
    client_id = job.user_id
    context['client_id'] = client_id
    context['job'] = job
    if Notification.objects.all().count() > 0:
        notification = Notification.objects.all().order_by("-id")[0]
        notification_count = notification.id+1
    else:
        notification_count = 1
    if request.POST:
        form = RequestBid(request.POST)
        if form.is_valid():
            a = form.save(commit=False)
            a.job_id = job_id
            a.save()
            job_bid_id = JobBid.objects.all().order_by("-id")[0].id
            username = request.user.username
            sender = request.user.id
            receiver = client_id
            message = "{} has applied a bid to a task {}.".format(username,job.job_title)
            link = reverse('view_bid', args=[str(job_bid_id), str(notification_count)])
            notification = Notification(message=message, receiver_id=receiver, sender_id=sender, link=link)
            notification.save()
            return redirect('view_job')
        else:
            context['bid_job'] = form
    else:
        form = RequestBid()
        context['bid_job'] = form
    return render(request, 'job/bid_job.html', context)

@login_required
@csrf_exempt
def view_bid(request, job_bid_id, notification_id):
    context={}
    query = JobBid.objects.raw('SELECT * from job_jobbid jb join job_job j on jb.job_id = j.id;')
    job_title = query[0].job_title
    notification = Notification.objects.get(id = notification_id)
    if request.user.user_type == "client" and notification.read == False:
        notification.read = True
        notification.save()
    bid_data = JobBid.objects.get(id=job_bid_id)
    
    if request.POST:
        form = AcceptBid(request.POST)
        if form.is_valid():
            #saving accepted jobs
            a = form.save(commit = False)
            a.client_id = notification.receiver_id
            a.freelancer_id = notification.sender_id
            a.job_id = bid_data.job_id
            a.save()
            
            #saving notification for freelancer
            count = Notification.objects.all().order_by("-id")[0]
            notification_count = count.id+1
            sender = request.user.id
            receiver = notification.sender_id
            message = "{} has approved your bid on a task {}.".format(request.user.username, job_title)
            link = reverse('view_bid', args=[str(job_bid_id), str(notification_count)])
            notification = Notification(message=message, receiver_id=receiver, sender_id=sender, link=link)
            notification.save()
            return redirect('view_job')
        else:
            form = AcceptBid()
            context['form'] = form
    context['bid_data'] = bid_data
    return render(request, 'job/view_bid.html', context)
