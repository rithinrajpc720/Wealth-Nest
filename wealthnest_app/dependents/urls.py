from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dependent_dashboard'),
    path('chores/', views.chores, name='dependent_chores'),
    path('chores/<int:pk>/complete/', views.chore_complete, name='dependent_chore_complete'),
    path('spending/', views.spending, name='dependent_spending'),
    path('spending/<int:pk>/delete/', views.expense_delete, name='dependent_expense_delete'),
    path('goals/', views.goals, name='dependent_goals'),
    path('goals/<int:pk>/contribute/', views.goal_contribute, name='dependent_goal_contribute'),
    path('goals/<int:pk>/delete/', views.goal_delete, name='dependent_goal_delete'),
    path('progress/', views.progress, name='dependent_progress'),
    path('balance/', views.balance, name='dependent_balance'),
    path('profile/', views.profile, name='dependent_profile'),
]
