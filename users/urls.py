from django.urls import path
from users.views import CustomLoginView, EmailCheckView, SuccessLoginView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('success_login/', SuccessLoginView.as_view(), name='success_login'),
    path('register/', EmailCheckView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]