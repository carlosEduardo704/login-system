from django import forms
from users.models import CustomUser, OtpToken
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginRegisterForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = get_user_model()
        fields = ['email']


class RegisterForm(UserCreationForm):
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(),
        label='Password'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(),
        label='Confirm password'
    )
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email',)


    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'


class OtpVerificationForm(forms.Form):
    otp_code = forms.CharField(max_length=6, label='Enter your verication code')

    class Meta:
        fields = ['otp_code']


class ResendOptCodeForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'Email'}),)

    class Meta:
        fields = ['email']

        labels = {
            'email': 'Email'
        }