from django.shortcuts import render

# Create your views here.


def post_job(request):
    return render(request, 'job/post_job.html')