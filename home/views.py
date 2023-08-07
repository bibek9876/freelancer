from django.shortcuts import render
from job.models import Job
from account.models import Account

# Create your views here.


def home_page(request):
    context = {}
    
    user = request.user
    freelancers = Account.objects.filter(user_type = 'freelancer')
    job_list = Job.objects.all()
    if user.is_authenticated:
        user_type = user.user_type
        context['user_type'] = user_type
    context["job_list"] = job_list
    context["freelancers"] = freelancers
    return render(request, 'home/home.html', context)