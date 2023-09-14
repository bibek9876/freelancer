import os
import pdb
from django.shortcuts import render, redirect
from job.models import Job
from account.models import Account
from home.forms import ContactForm
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.contrib import messages

from django.contrib.postgres.search import SearchVector
from home.decorators import resume_required
# Create your views here.

def home_page(request):
    context = {}
    # pdb.set_trace()
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
    result = Job.objects.annotate(search=SearchVector("job_title", "description")).filter(search=request.GET['query'])
    context['results'] = result
    return render(request, 'home/search_result.html', context)

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
            pdb.set_trace()
            return redirect('contact')
        context['form'] = form
    else:
        form=ContactForm()
        context['form'] = form
    return render(request, 'home/contact.html', context)