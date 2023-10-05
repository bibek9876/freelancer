from django import forms

from job.models import Job, JobBid, AgreedJob, RejectionReason 

class PostJob(forms.ModelForm):
    class Meta:
        model =Job
        fields = ('user','job_title', 'image', 'price_per', 'project_length', 'rate', 'description', 'completion_time', 'category', 'freelancer_experience')
    
class ApplyJob(forms.ModelForm):
    class Meta:
        model= Job
        fields = ('rate', 'completion_time', 'price_per')
        
class EditJob(forms.ModelForm):
    class Meta:
        model = Job
        fields= (
            'job_title',
            'image',
            'rate',
            'description',
            'completion_time',
            'task_type',
        )
        
class RequestBid(forms.ModelForm):
    class Meta:
        model = JobBid
        fields = ('freelancer', 'client', 'rate', 'price_per', 'completion_time')
        
class AcceptBid(forms.ModelForm):
    class Meta:
        model = AgreedJob
        fields = ()
        
class RejectBid(forms.ModelForm):
    class Meta:
        model = RejectionReason
        fields = ('reason','reject_option',)