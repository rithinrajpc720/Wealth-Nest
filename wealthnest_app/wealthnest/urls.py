from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from accounts import views as account_views

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', account_views.landing, name='landing'),
    path('accounts/', include('accounts.urls')),
    path('admin-panel/', include('admin_panel.urls')),
    path('heads/', include('heads.urls')),
    path('dependents/', include('dependents.urls')),
    path('chores/', include('chores.urls')),
    path('transactions/', include('transactions.urls')),
    path('goals/', include('goals.urls')),
    path('achievements/', include('achievements.urls')),
    path('complaints/', include('complaints.urls')),
    path('feedback/', include('feedback.urls')),
    path('chatbot/', include('chatbot.urls')),
]

handler404 = 'accounts.views.handler404'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
