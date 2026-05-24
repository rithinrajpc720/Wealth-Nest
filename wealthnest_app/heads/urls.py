from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='head_dashboard'),
    path('chores/', views.chore_manager, name='head_chores'),
    path('chores/create/', views.chore_create, name='head_chore_create'),
    path('chores/<int:pk>/edit/', views.chore_edit, name='head_chore_edit'),
    path('chores/<int:pk>/delete/', views.chore_delete, name='head_chore_delete'),
    path('chores/<int:pk>/archive/', views.chore_archive, name='head_chore_archive'),
    path('accounts/', views.accounts, name='head_accounts'),
    path('accounts/<int:dep_id>/adjust/', views.balance_adjust, name='head_balance_adjust'),
    path('accounts/<int:dep_id>/allowance/', views.allowance_set, name='head_allowance'),
    path('approvals/', views.approvals, name='head_approvals'),
    path('approvals/<int:pk>/approve/', views.approve_chore, name='head_approve_chore'),
    path('approvals/<int:pk>/reject/', views.reject_chore, name='head_reject_chore'),
    path('spend/', views.spend_logs, name='head_spend'),
    path('analytics/', views.analytics, name='head_analytics'),
    path('profile/', views.profile, name='head_profile'),
]
