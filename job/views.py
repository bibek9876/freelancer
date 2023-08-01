from django.shortcuts import render, redirect
from job.forms import PostJob
from job.models import Job
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
import pdb
@csrf_exempt
def post_job(request):
    context= {}
    user = request.user.id
    context['user'] = user
    if request.POST:
        form = PostJob(request.POST)
        if form.is_valid():
            
            form.save()
            return redirect('home')
        else:
            context['post_job'] = form
    else:
        form = PostJob()
        context['post_job'] = form
    return render(request, 'job/post_job.html', context)

def view_jobs(request):
    context = {}
    user_id = request.user.id
    jobs = Job.objects.filter(user_id=user_id)
    # pdb.set_trace()
    context['jobs'] = jobs
    return render(request, 'job/view_jobs.html', context)