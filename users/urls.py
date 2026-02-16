from django.urls import path
from users.views import RegisterView, VerifyEmailView, ResendOtpCodeView, CustomLoginView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify_email/<str:url_code>/<str:email>', VerifyEmailView.as_view(), name='verify_email'),
    path('resend_code/', ResendOtpCodeView.as_view(), name='resend_code')
]