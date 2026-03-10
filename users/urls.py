from django.urls import path
from users.views import CustomLoginView, EmailCheckView, SuccessLoginView, HomePageView, ForgotPasswordView, UpdatePassordView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('success_login/', SuccessLoginView.as_view(), name='success_login'),
    path('register/', EmailCheckView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('forgot_password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('update_password/<str:email>/<str:url_code>/', UpdatePassordView.as_view(), name='update_password')
]