# CBViews
from django.views.generic import CreateView, FormView
# Forms
from users.forms import RegisterForm, LoginRegisterForm, OtpVerificationForm, ResendOptCodeForm
# Models
from django.contrib.auth import get_user_model
from users.models import CustomUser, OtpToken
# ...
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.password_validation import password_validators_help_texts
from django.utils import timezone
from django.core.mail import send_mail
from django.http import Http404
class LoginRegisterView(FormView):
    template_name = 'login_register.html'
    form_class = LoginRegisterForm

    def form_valid(self, form):
        email = form.cleaned_data['email']

        User = get_user_model().objects.get(email=email)

        if User:
            if User.is_active:
                return redirect('login')
            else:
                return redirect('verify_email', email=email)
        else:
            return redirect('register')

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'signup.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        email = form.cleaned_data['email']
        self.success_url = reverse_lazy('verify_email', kwargs={'email': email})

        return super().form_valid(form)

    def form_invalid(self, form):
        email = form.cleaned_data['email']
        User = get_user_model()

        if User.objects.filter(email=email).exists():
            return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['password_rules'] = password_validators_help_texts()
        return context


class VerifyEmailView(FormView):
    form_class = OtpVerificationForm
    template_name = 'verify_email.html'
    
    def dispatch(self, request, *args, **kwargs):
        url_code = self.kwargs.get('url_code')
        user = get_user_model().objects.get(email=self.kwargs.get('email'))
        token = OtpToken.objects.filter(user=user).last().url_code

        if token != url_code:
            raise Http404()

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        email = self.kwargs.get('email')
        return get_user_model().objects.filter(email=email)

    def form_valid(self, form):
        code = form.cleaned_data['otp_code']
        email = self.kwargs.get('email')

        user = get_user_model().objects.get(email=email)
        otp_record = OtpToken.objects.filter(user=user).last()

        if code == otp_record.otp_code and otp_record.otp_expires_at > timezone.now():
            user.is_active = True
            user.save()
            
            return redirect('login') 
        else:
            form.add_error('otp_code', 'Code invalid or expired.')
            return super().form_invalid(form)


class ResendOtpCodeView(FormView):
    form_class = ResendOptCodeForm
    template_name = 'resend_code.html'

    def form_valid(self, form):
        email = form.cleaned_data['email']
        user = get_user_model().objects.get(email=email)

        self.success_url = reverse_lazy('verify_email', kwargs={'email': email})

        if user:
            today_tokens = OtpToken.objects.filter(otp_created_at__date=timezone.localdate()).count()

            if today_tokens > 2:
                form.add_error('email', 'Maximum number of tokens per day rechead! Try again tomorrow!')
                return super().form_invalid(form)

            OtpToken.create_new_opt_code(user=user)
            OtpToken.send_email(user)
            return super().form_valid(form)
            
        else:
            form.add_error('email', 'invalid email')
            return super().form_invalid(form)
