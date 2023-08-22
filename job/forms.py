from django import forms

from job.models import Job, JobBid, AgreedJob

class PostJob(forms.ModelForm):
    class Meta:
        model =Job
        fields = ('user','job_title', 'image', 'rate', 'hour', 'description', 'completion_time', 'task_type')
        
class RequestBid(forms.ModelForm):
    class Meta:
        model = JobBid
        fields = ('freelancer', 'client', 'requested_rate', 'requested_hour', 'requested_completion_time')
        
class AcceptBid(forms.ModelForm):
    class Meta:
        model = AgreedJob
        fields = ('agreed_rate', 'agreed_hour', 'agreed_completion_time',)