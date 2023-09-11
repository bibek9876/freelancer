from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponse
from account.models import Account, Resume
import pdb

# def check_resume(user):
#     resume_count = Resume.objects.filter(freelancer_id=user.id).count()
#     # pdb.set_trace()
#     if user.user_type == "freelancer" and resume_count < 1:
#         return True
#     return False

# def resume_required():
#     def decorator(view):
#         @wraps(view)
#         def _wrapped_view(request, *args, **kwargs):
#             resume_count = Resume.objects.filter(freelancer_id=request.user.id)
#             user_type = request.user.user_type
#             pdb.set_trace()
#             if not check_resume(request.user):
#                 return redirect("build_resume", request.user.id)
#             return view(request, *args, **kwargs)
#         return _wrapped_view
#     return decorator


def resume_required(view_func):
    @wraps(view_func)  # This ensures that the original view function's attributes are preserved.
    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        
        resume_count = Resume.objects.filter(freelancer_id=request.user.id).count()
        user_type = request.user.user_type
        
        if user_type == "freelancer" and resume_count < 1:
            return redirect("build_resume", request.user.id)
        # Call the original view function
        # pdb.set_trace()

        return response

    return wrapper