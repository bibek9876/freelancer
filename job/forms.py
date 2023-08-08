from django import forms

from job.models import Job, JobBid

class PostJob(forms.ModelForm):
    class Meta:
        model =Job
        fields = ('user','job_title', 'rate', 'hour', 'description', 'completion_time')
        
class RequestBid(forms.ModelForm):
    class Meta:
        model = JobBid
        fields = ('freelancer', 'client', 'requested_rate', 'requested_hour', 'requested_completion_time')