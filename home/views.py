from django.shortcuts import render
import pdb

# Create your views here.


def home_page(request):
    context = {}
    
    user = request.user
    if user.is_authenticated:
        user_type = user.user_type
        context['user_type'] = user_type
    return render(request, 'home/home.html', context)
