from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot, name='chatbot'),
    path('send/', views.send_message, name='chatbot_send'),
    path('new/', views.new_chat, name='chatbot_new'),
    path('session/<int:pk>/', views.load_session, name='chatbot_session'),
]
