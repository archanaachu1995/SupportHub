"""
URL configuration for mainproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from SupportHub import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path("",views.home,name="Home"),
    path('register/',views.register,name='register'),
    path('login/',views.user_login,name='login'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('register_complaint/', views.register_complaints, name='register_complaints'),
    path('Pending_complaints/',views.pending_complaints,name='Pending'),
    path('Resolved_complaints/',views.resolved_complaints,name='Resolved'),
    path('reports/', views.user_reports, name='user_reports'),
    path('reports/download/<int:report_id>/', views.download_report, name='download_report'),
    path('reports/<int:report_id>/view/', views.view_report, name='view_report'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('track-complaints/', views.track_complaints, name='track_complaints'),
    path('settings/', views.user_settings, name='settings'),
    
    path('settings/', views.user_settings, name='user_settings'),
    path('logout/', views.logout_view, name='logout'),
    path('newlogin',views.login_login,name='newlogin'),



]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
