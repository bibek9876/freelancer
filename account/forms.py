from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate

from account.models import Account

class FreelancerRegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=60, help_text="Required. Add a valid email address.")
    class Meta:
        model = Account
        fields = (
            "user_type",
            "email", 
            "username", 
            "first_name", 
            "last_name", 
            "title", 
            "skills", 
            "country", 
            "bio", 
            "languages", 
            "phone_number",
            "password1", 
            "password2"
        )
        
class UserLoginForm(forms.ModelForm):
    
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    
    class Meta:
        model =Account
        fields = ('email', 'password')
        
    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email = email, password = password):
                raise forms.ValidationError('Email and password does not match.')
            
class AccountupdateForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = (
            'first_name',
            'last_name',
            'country',
            'bio',
        )
        
class ImageUpdateForm(forms.ModelForm):
    class Meta:
        model=Account
        fields=('profile_image',)