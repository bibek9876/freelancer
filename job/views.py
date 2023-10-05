
import os
from django.shortcuts import render, redirect, get_object_or_404
from job.forms import PostJob, RequestBid, AcceptBid, RejectBid, EditJob, ApplyJob
from job.models import Job, JobBid, AgreedJob, RejectionReason, JobCategories, JobSubCategories, JobApplies, UserPayment
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, JsonResponse, HttpResponse
from account.models import Account
from notification.models import Notification
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from django.core.management.color import no_style
from django.db import connection

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


import stripe
from django.conf import settings
import time

# Create your views here.

def must_authenticate(request):
    context = {}
    return render(request, 'account/must_authenticate.html', context)

@csrf_exempt
def get_sub_categories(request):
    if request.POST.get('category') != "" and request.POST:
        sub_category= JobSubCategories.objects.filter(job_categories_id = request.POST.get('category'))
        sub_category_list=[]
        for category in sub_category:
            sub_category_list.append({
                                        "category_id": category.id,
                                        "category_name": category.sub_category_name
                                    })
        response = {
            'sub_categories' : sub_category_list,
        }
        return JsonResponse(response)
    
@csrf_exempt
def post_job(request):
    context= {}
    user = request.user
    job_categories = JobCategories.objects.all()
    job_sub_categories = JobSubCategories.objects.all()
    context['categories'] = job_categories
    context['sub_categories'] = job_sub_categories
    if not user.is_authenticated:
        return redirect('must_authenticate')
    else:
        user_id = user.id
        context['user'] = user_id
        if request.POST:
            form = PostJob(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('home')
            else:
                context['post_job'] = form
        else:
            form = PostJob()
            context['post_job'] = form
    return render(request, 'job/post_job.html', context)

@login_required
def edit_jobs(request, job_id):
    context={}
    job = Job.objects.get(id=job_id)
    if request.POST:
        form = EditJob(request.POST)
        if form.is_valid():
            image_path = job.image.path
            if os.path.exists(image_path):
                os.remove(image_path)
            job.job_title = request.POST['job_title']
            job.rate = request.POST['rate']
            job.hour = request.POST['hour']
            job.description = request.POST['description']
            job.completion_time = request.POST['completion_time']
            job.image = request.POST['image']
            job.save()
            context['form'] = form
        else:
            context['form'] = form
    else:
        form = EditJob()
        context['form'] = form
    context['job'] = job
    return render(request, 'job/edit_job.html', context)

def view_jobs(request):
    context = {}
    user = request.user
    jobs = Job.objects.filter()
    categories = JobSubCategories.objects.all()
    paginator = Paginator(jobs, 2)
    page_number = request.GET.get('page')
    total_page = paginator.get_page(page_number)
    number_of_pages = total_page.paginator.num_pages
    if user.is_authenticated:
        if user.user_type == "client":
            jobs = Job.objects.filter(user_id=user.id).filter(job_status="not assigned")
        else:
            jobs = Job.objects.filter(job_status="not assigned")
    else:
        jobs = Job.objects.filter(job_status="not assigned")
    context['categories'] = categories
    context['total_page'] = total_page
    context['last_page'] = number_of_pages
    context['pages'] = [n+1 for n in range(number_of_pages)]
    context['jobs'] = total_page
    context['result_count'] = jobs.count()
    return render(request, 'job/view_jobs.html', context)

def job_pagination(request, page):
    context= {}
    jobs = Job.objects.all()
    p = Paginator(jobs, 5)
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        page_obj = p.page(1)
    except EmptyPage:
        # if page is empty then return last page
        page_obj = p.page(p.num_pages)
    context['page_obj'] = page_obj
    
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
    client_id = job_detail.user_id
    context['client_id'] = client_id
    # get_job = Job.objects.get(id = job_id)
    if request.POST:
        if request.POST.get('rate'): #Bidding job
            
            if Notification.objects.all().count() > 0:
                notification = Notification.objects.all().order_by("-id")[0]
                notification_count = notification.id+1
            else:
                sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Notification])
                with connection.cursor() as cursor:
                    for sql in sequence_sql:
                        cursor.execute(sql)
                notification_count = 1
            form = RequestBid(request.POST)
            if form.is_valid():
                a = form.save(commit=False)
                a.job_id = job_id
                a.save()
                job_bid_id = JobBid.objects.all().order_by("-id")[0].id
                username = request.user.username
                sender = request.user.id
                receiver = client_id
                message = "{} has applied a bid to a task {}.".format(username,job_detail.job_title)
                link = reverse('view_bid', args=[str(job_bid_id), str(notification_count)])
                notification = Notification(message=message, receiver_id=receiver, sender_id=sender, link=link)
                notification.save()
                return redirect('view_job')
            else:
                context['bid_job'] = form
        #end of bidding job
        
        # start of apply job
        else: 
            job_apply = JobApplies.objects.create(
                client_id=client_id,
                freelancer_id = request.user.id,
                job_id = job_id,
                status = "requested"
            )
            job_apply.save()
            return redirect('view_job')
        # end of apply job
    return render(request, 'job/apply_jobs.html', context)

# @login_required
# @csrf_exempt
# def bid_job(request, job_id):
#     context={}
#     job = Job.objects.get(id = job_id)
#     client_id = job.user_id
#     context['client_id'] = client_id
#     context['job'] = job
#     if Notification.objects.all().count() > 0:
#         notification = Notification.objects.all().order_by("-id")[0]
#         notification_count = notification.id+1
#     else:
#         sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Notification])
#         with connection.cursor() as cursor:
#             for sql in sequence_sql:
#                 cursor.execute(sql)
#         notification_count = 1
#     if request.POST:
#         form = RequestBid(request.POST)
#         if form.is_valid():
#             a = form.save(commit=False)
#             a.job_id = job_id
#             a.save()
#             job_bid_id = JobBid.objects.all().order_by("-id")[0].id
#             username = request.user.username
#             sender = request.user.id
#             receiver = client_id
#             message = "{} has applied a bid to a task {}.".format(username,job.job_title)
#             link = reverse('view_bid', args=[str(job_bid_id), str(notification_count)])
#             notification = Notification(message=message, receiver_id=receiver, sender_id=sender, link=link)
#             notification.save()
#             return redirect('view_job')
#         else:
#             context['bid_job'] = form
#     else:
#         form = RequestBid()
#         context['bid_job'] = form
#     return render(request, 'job/bid_job.html', context)


def checkout(request, job_id, bid_id, notification_id):
    context = {}
    job = Job.objects.get(id=job_id)
    job = JobBid.objects.get(id=bid_id)
    context['job_id'] = job_id
    context['job_bid_id'] = bid_id
    context['job'] = job
    context['notification_id'] = notification_id
    # 
    return render(request, 'payment/payment.html', context)

def checkout_session(request):
    job_details = Job.objects.get(id=request.POST.get('job_id'))
    job_bid_details = JobBid.objects.get(id=request.POST.get('job_bid_id'))
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        product = stripe.Product.create(
            name=job_details.job_title,
            description=job_details.description,
            type='service',  # You can specify 'service', 'good', or 'sku'
         )
        price = stripe.Price.create(
            unit_amount = int(job_bid_details.rate) * 100,
            currency= 'AUD',
            product = product.id
        )
        checkout_session = stripe.checkout.Session.create(
            payment_method_types = ['card'],
            line_items = [
                {
                    'price': price.id,
                    'quantity': 1,
                },
            ],
            mode = 'payment',
            metadata = {'job_id': job_details.id,
                        'job_bid_id': job_bid_details.id,
                        'agreed_rate': job_bid_details.rate,
                        'agreed_completion_time': job_bid_details.completion_time,
                        'agreed_price_per': job_bid_details.price_per,
                        'notification_id': request.POST.get('notification_id'),
                        'user_type': request.user.user_type,
                        'user_id': request.user.id,
                        },
            customer_creation = 'always',
            success_url= settings.REDIRECT_DOMAIN + '/jobs/payment_checkout_success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url = settings.REDIRECT_DOMAIN + '/payment_canceled',
        )
        return redirect(checkout_session.url, job_bid_details, code=303)
        # try:
        #     # Get the token from the request
        #     token = request.POST['stripeToken']
            
        #     # Create a charge
        #     charge = stripe.Charge.create(
        #         amount=1000,  # Amount in cents (e.g., $10.00)
        #         currency='usd',
        #         description='Example charge',
        #         source=token,
        #     )
            
        #     # Handle successful payment (e.g., update database, send email, etc.)
        #     return redirect('payment_success')
        # except stripe.error.CardError as e:
        #     # Handle card errors (e.g., display an error message)
        #     return JsonResponse({'error': e.user_message})
        # except Exception as e:
        #     # Handle other errors
        #     return JsonResponse({'error': 'An error occurred.'})
    return render(request, 'payment/payment.html')

@login_required
@csrf_exempt
def view_bid(request, job_bid_id, notification_id):
    context={}
    user = request.user
    
    if user.user_type != "client":
        return render(request, 'home/not_a_client.html')
    else:
        bid_data = JobBid.objects.get(id=job_bid_id)
        job_data = Job.objects.filter(id=bid_data.job_id).select_related() 
        notification = Notification.objects.get(id = notification_id)
        freelancer_details = Account.objects.get(id=notification.sender_id)
        context["freelancer_details"] = freelancer_details
        job_id = bid_data.job_id
        # agreed_job = AgreedJob.objects.filter(job_id=job_id)
        # if agreed_job.count() < 1:
        #     query = JobBid.objects.raw('SELECT * from job_jobbid jb join job_job j on jb.job_id = j.id;')
        #     job_title = query[0].job_title
        #     notification = Notification.objects.get(id = notification_id)
        #     if request.user.user_type == "client" and notification.read == False:
        #         notification.read = True
        #         notification.save()
            
            
        # else:
        #     return redirect('view_job')
        
        context['bid_data'] = bid_data
        context['job_bid_id'] = job_bid_id
        context['notification_id'] = notification_id
        return render(request, 'job/view_bid.html', context)

def payment_successful(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return render(request, 'payment/successful_payment.html')

def payment_canceled(request):
    return render(request, 'payment/failure_payment.html')

@csrf_exempt
def stripe_webhook(request):
    context = {}
    stripe.api_key = settings.STRIPE_SECRET_KEY
    time.sleep(10)
    payload = request.body
    signature_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, signature_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationerror as e:
        return HttpResponse(status=400)
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get('id', None)
        
        
        #Approving jobs after payment
        query = JobBid.objects.raw('SELECT * from job_jobbid jb join job_job j on jb.job_id = j.id;')
        job_title = query[0].job_title
        notification = Notification.objects.get(id = session["metadata"]["notification_id"])
        agreed_job = AgreedJob.objects.filter(job_id=session["metadata"]["job_id"])
        if agreed_job.count() < 1:
            if session["metadata"]["user_type"] == "client" and notification.read == False:
                notification.read = True
                notification.save()
                
        form = AcceptBid(request.POST)
        job = Job.objects.get(id=session["metadata"]["job_id"])
        job_bid = JobBid.objects.get(id=session["metadata"]["job_bid_id"])
        if form.is_valid():
            #saving accepted jobs
            a = form.save(commit = False)
            a.client_id = notification.receiver_id
            a.agreed_rate = session["metadata"]["agreed_rate"]
            a.agreed_price_per = session["metadata"]["agreed_price_per"]
            a.agreed_completion_time = session["metadata"]["agreed_completion_time"]
            a.freelancer_id = notification.sender_id
            a.job_id = session["metadata"]["job_id"]
            a.save()
                        
            #changing status in job table
            job.job_status = "assigned"
            job.save()
                        
            #changing status in job bid table
            job_bid.status = "approved"
            job_bid.save()
                        
            #saving notification for freelancer
            count = Notification.objects.all().order_by("-id")[0]
            notification_count = count.id+1
            sender = session["metadata"]["user_id"]
            receiver = notification.sender_id
            message = "{} has approved your bid on a task {}.".format(request.user.username, job_title)
            link = reverse('view_bid', args=[str(session["metadata"]["job_bid_id"]), str(notification_count)])
            notification = Notification(message=message, receiver_id=receiver, sender_id=sender, link=link)
            notification.save()
            return redirect('view_job')
        else:
            form = AcceptBid()
            context['form'] = form
        time.sleep(15)
    
    return HttpResponse(status=200)
        
    

@csrf_exempt
def reject_bid(request, job_bid_id, freelancer_id):
    context={}
    client_id = request.user.id
    job_id = JobBid.objects.get(id=job_bid_id).job_id
    job_title = Job.objects.get(id=job_id).job_title
    if request.method == "POST":
        job_bid = JobBid.objects.get(id = job_bid_id)
        form = RejectBid()
        a = form.save(commit=False)
        a.client_id = client_id
        a.freelancer_id = freelancer_id
        a.job_id = job_id
        a.reason = request.POST['reason']
        a.reject_option = request.POST['reject_option']
        a.save()
        
        #changing status in job bid table
        job_bid.status = "rejected"
        job_bid.save()
        
        # Saving notification
        count = Notification.objects.all().order_by("-id")[0]
        notification_count = count.id+1
        message = "{} has rejected your bid on a task {}.".format(request.user.username, job_title)
        link = reverse('apply_job', args=[str(job_id)])
        notification = Notification(message=message, receiver_id=freelancer_id, sender_id=client_id, link=link)
        notification.save()
        return redirect('view_job')
    return render(request, 'job/reject_bid.html', context)

@csrf_exempt
def search_job(request):
    context = {}
    result = Job.objects.filter(body_text__search="cheese")

@login_required
def delete_job(request, job_id):
    context = {}
    job = Job.objects.get(id = job_id)
    job.delete()
    return redirect('view_job')
