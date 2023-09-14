from django import forms

from job.models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model=Contact
        fields=(
            "name",
            "email",
            "phone",
            "message",
        )