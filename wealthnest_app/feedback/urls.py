from django.urls import path
from . import views

urlpatterns = [
    path('head/', views.head_feedback, name='head_feedback'),
    path('dependent/', views.dependent_feedback, name='dependent_feedback'),
]
