from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from users.models import OtpToken
from django.utils import timezone
from django.core.exceptions import ValidationError

class CheckEmailForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email']

        user, created = get_user_model().objects.get_or_create(email=email)

        # Otp_code creating limit
        start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timezone.timedelta(days=1)

        user_otp_create_today = OtpToken.objects.filter(user=user,
            otp_created_at__gte=start,
            otp_created_at__lt=end).count()

        if user_otp_create_today > 3:
            raise ValidationError(
                "Too many attempts. You rechead the OTP code limit today. Try again tomorrow."
            )
        
        return email

    class Meta:
        fields = ['email',]

class OtpVerificationForm(forms.Form):
    otp_code = forms.CharField(max_length=6, label='')

    class Meta:
        fields = ['otp_code']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['otp_code'].widget.attrs['placeholder'] = 'OTP Code'