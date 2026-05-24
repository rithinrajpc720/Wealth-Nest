from django.urls import path
from . import views

urlpatterns = [
    path('head/', views.head_complaints, name='head_complaints'),
    path('head/create/', views.head_complaint_create, name='head_complaint_create'),
    path('dependent/', views.dependent_complaints, name='dependent_complaints'),
    path('dependent/create/', views.dependent_complaint_create, name='dependent_complaint_create'),
]
