from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='admin_dashboard'),
    path('enrollment/', views.enrollment, name='admin_enrollment'),
    path('enrollment/<int:pk>/', views.family_view, name='admin_family_view'),
    path('enrollment/<int:pk>/toggle/', views.family_toggle, name='admin_family_toggle'),
    path('telemetry/', views.telemetry, name='admin_telemetry'),
    path('complaints/', views.admin_complaints, name='admin_complaints'),
    path('complaints/<int:pk>/resolve/', views.admin_complaint_resolve, name='admin_complaint_resolve'),
    path('feedback/', views.admin_feedback, name='admin_feedback'),
    path('categories/', views.categories, name='admin_categories'),
    path('categories/<str:kind>/create/', views.category_create, name='admin_category_create'),
    path('categories/<str:kind>/<int:pk>/delete/', views.category_delete, name='admin_category_delete'),
]
