from django.shortcuts import render

# Create your views here.


def home_page(request):
    context = {}
    context["some_string"] = "Hi, this is my practice page."
    
    list_of_strings = []
    list_of_strings.append("First")
    list_of_strings.append("Second")
    list_of_strings.append("Third")
    list_of_strings.append("Fourth")
    
    context["list_of_string"] = list_of_strings
    return render(request, 'home/home.html', context)