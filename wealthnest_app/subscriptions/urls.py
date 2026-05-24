from django.urls import path
from . import views

urlpatterns = [
    path('pricing/', views.pricing, name='subscription_pricing'),
    path('checkout/<slug:plan_slug>/<str:cycle>/', views.checkout, name='subscription_checkout'),
    path('pay/<slug:plan_slug>/<str:cycle>/', views.process_payment, name='subscription_pay'),
    path('success/<int:payment_id>/', views.payment_success, name='subscription_payment_success'),
    path('manage/', views.manage_subscription, name='subscription_manage'),
    path('cancel/', views.cancel_subscription, name='subscription_cancel'),
    path('history/', views.payment_history, name='subscription_history'),
    path('invoice/<int:payment_id>/', views.invoice, name='subscription_invoice'),
    path('admin/subscriptions/', views.admin_subscriptions, name='admin_subscriptions'),
    path('admin/payments/', views.admin_payments, name='admin_payments'),
]
