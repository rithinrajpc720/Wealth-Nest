from django.urls import path
from . import views

urlpatterns = [
    path('export-csv/', views.export_family_csv, name='export_family_csv'),
]
