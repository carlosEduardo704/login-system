from django import forms
from users.models import CustomUser, OtpToken
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginRegisterForm(forms.Form):
    email = forms.EmailField()

    class Meta:
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


class OtpVerificationForm(forms.Form):
    otp_code = forms.CharField(max_length=6, label='OTP Code:')

    class Meta:
        fields = ['otp_code']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['otp_code'].widget.attrs['placeholder'] = 'OTP Code'


class ResendOptCodeForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(),)

    class Meta:
        fields = ['email']

        labels = {
            'email': 'Email'
        }