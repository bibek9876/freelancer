from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate

from account.models import Account, Resume, AdminDetails

class AdminSaveAccount(UserCreationForm):
    class Meta:
        model=Account
        fields=(
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

class AdminRegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=60, help_text="Required. Add a valid email address.")
    class Meta:
        model=AdminDetails
        fields=(
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

class VerifyToken(forms.ModelForm):
    class Meta:
        model = AdminDetails
        fields=(
            "token",
        )
        
class FreelancerRegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=60, help_text="Required. Add a valid email address.")
    class Meta:
        model = Account
        fields = (
            "email", 
            "username", 
            "first_name", 
            "last_name", 
            "title",  
            "phone_number",
            "country",
            "password1", 
            "password2"
        )
        
class ClientRegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=60, help_text="required. Add a valid Email address.")
    class Meta:
        model=Account
        fields = (
            'first_name',
            'last_name',
            'username',
            'country',
            'email',
            'password1',
            'password2',
        )

class AdminLoginForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    class Meta:
        model =AdminDetails
        fields = ('email', 'password')
    # def clean(self):
    #     if self.is_valid():
    #         email = self.cleaned_data['email']
    #         password = self.cleaned_data['password']
    #         if not authenticate(email = email, password = password):
    #             raise forms.ValidationError('Email and password does not match.')
            
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
        )
        
class ImageUpdateForm(forms.ModelForm):
    class Meta:
        model=Account
        fields=('profile_image',)
        
class CreateResume(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ('title', 'bio', 'languages', 'skills')