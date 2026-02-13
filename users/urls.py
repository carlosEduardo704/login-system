from django.urls import path
from users.views import RegisterView, LoginRegisterView, VerifyEmailView, ResendOtpCodeView, CustomLoginView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login_register/', LoginRegisterView.as_view(), name='login_register'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify_email/<str:url_code>/<str:email>', VerifyEmailView.as_view(), name='verify_email'),
    path('resend_code/', ResendOtpCodeView.as_view(), name='resend_code')
]