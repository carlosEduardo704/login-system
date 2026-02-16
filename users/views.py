# CBViews
from django.views.generic import CreateView, FormView
from django.contrib.auth.views import LoginView
# Forms
from users.forms import RegisterForm, OtpVerificationForm, ResendOptCodeForm
# Models
from django.contrib.auth import get_user_model
from users.models import OtpToken
# ...
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.password_validation import password_validators_help_texts
from django.utils import timezone
from django.http import Http404
from django.contrib import messages

class LoginRegisterView(FormView):
    template_name = 'login_register.html'
    form_class = LoginRegisterForm

    def form_valid(self, form):
        email = form.cleaned_data['email']
        self.request.session['email'] = email

        qs = get_user_model().objects.filter(email=email)

        if qs:
            user = get_user_model().objects.get(email=email)
            if user.is_active:
                return redirect('login')
            else:
                url_code = OtpToken.objects.filter(user=user).last().url_code
                return redirect('verify_email', url_code=url_code, email=email)
        else:
            return redirect('register')


class CustomLoginView(LoginView):
    template_name='login.html'

    def get_initial(self):
        initial = super().get_initial()

        email = self.request.session.pop('email', None)

        if email:
            initial['username'] = email
        
        return initial

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'signup.html'

    def get_initial(self):
        initial = super().get_initial()

        email = self.request.session.pop('email', None)

        if email:
            initial['email'] = email
        
        return initial

    def form_valid(self, form):
        email = form.cleaned_data['email']
        qs = get_user_model().objects.filter(email=email)

        if qs:
            return redirect('login')
        else:
            user = form.save(commit=False)
            user.save()

            url_code = OtpToken.objects.filter(user=email).last().url_code
            self.success_url = reverse_lazy('verify_email', kwargs={'url_code': url_code, 'email': email})

            return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['password_rules'] = password_validators_help_texts()
        return context


class VerifyEmailView(FormView):
    form_class = OtpVerificationForm
    template_name = 'verify_email.html'
    success_url = reverse_lazy('login')
    
    def dispatch(self, request, *args, **kwargs):
        user_email = self.kwargs.get('email')
        url_code = self.kwargs.get('url_code')

        user = get_user_model().objects.get(email=user_email)
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
            
            messages.success(self.request, "The user was successfully verified!")
            return super().form_valid(form)
        else:
            form.add_error('otp_code', 'Code invalid or expired.')
            return super().form_invalid(form)


class ResendOtpCodeView(FormView):
    form_class = ResendOptCodeForm
    template_name = 'resend_code.html'

    def form_valid(self, form):
        email = form.cleaned_data['email']
        qs = get_user_model().objects.filter(email=email)

        if not qs:
            form.add_error('email', 'invalid email')
            return super().form_invalid(form)

        user = get_user_model().objects.get(email=email)

        if user.is_active:
            form.add_error('email', 'This user is already active!')
            return super().form_invalid(form)

        number_of_tokens_today = OtpToken.objects.filter(user=user, otp_created_at__date=timezone.localdate()).count()

        if number_of_tokens_today > 2:
            form.add_error('email', 'Maximum number of tokens per day rechead! Try again tomorrow!')
            return super().form_invalid(form)

        OtpToken.create_new_opt_code(user=user)
        OtpToken.send_email(user)

        url_code = OtpToken.objects.filter(user=user).last().url_code
        self.success_url = reverse_lazy('verify_email', kwargs={'url_code': url_code, 'email': email})
        return super().form_valid(form)
