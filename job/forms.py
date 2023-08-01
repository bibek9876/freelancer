from django import forms

from job.models import Job

class PostJob(forms.ModelForm):
    class Meta:
        model =Job
        fields = ('user','job_title', 'rate', 'hour', 'description', 'completion_time')