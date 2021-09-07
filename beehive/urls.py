"""beehive URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from accounts import views
from django.conf import settings
from django.conf.urls.static import static
from user_management.views import ApprovalListView
from dashboard.views import NoticeBoardListView

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('', include('dashboard.urls')),
    path('approvals/', ApprovalListView.as_view(), name='approvals'),
    path('notice-board/', NoticeBoardListView.as_view(), name='notice_board'),
    path('cimplux-admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('employee/', include('employees.urls')),
    path('user-management/', include('user_management.urls')),
    path('self-service/', include('self_panel.urls', namespace='self_panel')),
    path('admin/', include('accounts.urls_admin')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
