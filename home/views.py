import pdb
from django.shortcuts import render
from job.models import Job
from account.models import Account
from django.views.decorators.csrf import csrf_exempt

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