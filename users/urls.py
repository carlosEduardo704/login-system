from django.urls import path
from users.views import RegisterView, LoginRegisterView, VerifyEmailView, ResendOtpCodeView
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('login_register/', LoginRegisterView.as_view(), name='login_register'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify_email/<str:url_code>/<str:email>', VerifyEmailView.as_view(), name='verify_email'),
    path('resend_code/', ResendOtpCodeView.as_view(), name='resend_code')
]