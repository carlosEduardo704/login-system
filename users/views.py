# CBViews
from django.views.generic import View, TemplateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
# Forms
from users.forms import OtpVerificationForm, CheckEmailForm
from django.contrib.auth.forms import SetPasswordForm
# Models
from django.contrib.auth import get_user_model, login as auth_login
from users.models import OtpToken
# ...
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.utils import timezone

class SuccessLoginView(LoginRequiredMixin, TemplateView):
    template_name = 'success_login.html'


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
                
                OtpToken.create_new_opt_code(user=user)
                OtpToken.send_email(user=user)
                
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
    
    
    def get_success_url(self):
        return reverse_lazy('success_login')

    def get_initial(self):
        initial = super().get_initial()

        email = self.request.session.pop('email', None)

        if email:
            initial['username'] = email
        
        return initial