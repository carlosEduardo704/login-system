from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from users.models import OtpToken
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'hello@exemple.com'}), label="Email")
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}), label="Password")

class CheckEmailForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email']

        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Invalid email format!")

        user, created = get_user_model().objects.get_or_create(email=email)

        # Otp_code creating limit
        start = timezone.now() - timezone.timedelta(minutes=20)
        end = timezone.now()

        user_otp_create_today = OtpToken.objects.filter(user=user,
            otp_created_at__gte=start,
            otp_created_at__lt=end).count()

        if user_otp_create_today > 3:
            raise ValidationError(
                "Too many attempts. Try again latter."
            )
        
        return email

    class Meta:
        fields = ['email',]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].widget.attrs['placeholder'] = 'hello@exemple.com'


class EmailCheckForgotPassword(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email']

        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Invalid email format!")
        
        return email

    class Meta:
        fields = ['email']

class OtpVerificationForm(forms.Form):
    otp_code = forms.CharField(max_length=6, label='')

    class Meta:
        fields = ['otp_code']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['otp_code'].widget.attrs['placeholder'] = 'OTP Code'