# CBViews
from django.views.generic import View, TemplateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
# Forms
from users.forms import OtpVerificationForm, CheckEmailForm, CustomAuthenticationForm, EmailCheckForgotPassword
from django.contrib.auth.forms import SetPasswordForm
# Models
from django.contrib.auth import get_user_model, login as auth_login
from users.models import OtpToken, UrlCodeOtp
# Tasks
from users.tasks import send_password_reset_user_email, send_otp_code_to_user_email
# ...
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.utils import timezone
from django.http import Http404
# Rate limit
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

class HomePageView(View):
    
    def dispatch(self, request):
        if not self.request.user.is_authenticated:
            return redirect('register')
        else:
            return redirect('success_login')

        return super().dispatch(request)

class SuccessLoginView(LoginRequiredMixin, TemplateView):
    template_name = 'success_login.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('register')

        return super().dispatch(request, *args, **kwargs)

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='dispatch')
class EmailCheckView(View):
    template_name = 'signup.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('success_login')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = CheckEmailForm()
        return render(request, self.template_name, {'form': form, 'step': 1})

    def post(self, request, *args, **kwargs):
        step = int(request.POST.get('step', 1))

        if step == 1:
            form = CheckEmailForm(request.POST)

            if form.is_valid():
                email = form.cleaned_data['email']

                user, created = get_user_model().objects.get_or_create(email=email)

                if created:
                    user.set_unusable_password()
                    user.save()
                
                send_otp_code_to_user_email.delay(user.pk)
                
                request.session['email'] = email

                form_two = OtpVerificationForm() 
                return render(request, self.template_name, {'form': form_two, 'step': 2})

        elif step == 2:
            form = OtpVerificationForm(request.POST)

            if form.is_valid():
                email = request.session.get('email')
                user = get_user_model().objects.get(email=email)

                code = form.cleaned_data['otp_code']
                user_opt_code = OtpToken.objects.filter(user=user).last()
                if code == user_opt_code.otp_code and user_opt_code.otp_expires_at > timezone.now():

                    if user.has_usable_password():
                        user.backend = 'django.contrib.auth.backends.ModelBackend'
                        auth_login(request, user)
                        del request.session['email']
                        return redirect('success_login')

                else:
                    form.add_error('otp_code', 'Code invalid or expired.')
                
                form_three = SetPasswordForm(user=user)

                return render(request, self.template_name, {'form': form_three, 'step': 3})

        elif step == 3:
            email = request.session.get('email')
            user = get_user_model().objects.get(email=email)
            form = SetPasswordForm(user=user, data=request.POST)

            if form.is_valid():
                user = form.save()
                auth_login(request, user)
                del request.session['email']
                return redirect('success_login')


        return render(request, self.template_name, {'form': form, 'step': step})


class CustomLoginView(LoginView):
    template_name='login.html'
    form_class = CustomAuthenticationForm
    
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('success_login')
        
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('success_login')

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='dispatch')
class ForgotPasswordView(View):
    template_name = 'forgot_password.html'

    def get(self, request, *args, **kwargs):
        form = EmailCheckForgotPassword()
        return render(request, self.template_name, {'form': form})

    
    def post(self, request, *args, **kwargs):
        form = EmailCheckForgotPassword(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']

            send_password_reset_user_email.delay(email)

            return render(request, self.template_name, {'success': True})

        return render(request, self.template_name, {'form': form})
        
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='dispatch')
class UpdatePassordView(View):
    template_name = 'update_password.html'


    def dispatch(self, request, *args, **kwargs):
        self.email = kwargs.get('email')
        self.code_on_url = kwargs.get('url_code')

        try:
            self.target_user = get_user_model().objects.get(email=self.email)
            user_last_url_code = UrlCodeOtp.objects.filter(user=self.target_user).last()
            
            if self.code_on_url != user_last_url_code.url_code or user_last_url_code.expires_at <= timezone.now():
                raise (Http404('Page Not Found!'))
                
        except get_user_model().DoesNotExist:
            raise Http404('Page not Found!')
            
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = SetPasswordForm(self.target_user, request.POST)

        if form.is_valid():
            form.save()

            obj = UrlCodeOtp.objects.get(url_code=self.code_on_url)
            obj.expires_at = timezone.now() - timezone.timedelta(minutes=1)
            obj.save()

            return redirect('login')
        
        return render(request, self.template_name, {'form': form})

        
    def get(self, request, *args, **kwargs):
        form = SetPasswordForm(self.target_user)
        return render(request, self.template_name, {'form': form})