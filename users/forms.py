from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

class CheckEmailForm(forms.Form):
    email = forms.EmailField()

    class Meta:
        fields = ['email',]

class OtpVerificationForm(forms.Form):
    otp_code = forms.CharField(max_length=6, label='')

    class Meta:
        fields = ['otp_code']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['otp_code'].widget.attrs['placeholder'] = 'OTP Code'