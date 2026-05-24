from django.urls import path
from . import views

urlpatterns = [
    path('head/register/', views.head_register, name='head_register'),
    path('head/login/', views.head_login, name='head_login'),
    path('dependent/register/', views.dependent_register, name='dependent_register'),
    path('dependent/login/', views.dependent_login, name='dependent_login'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
]
