"""
URL configuration for Postly project.

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
from django.urls import path,include
from django.shortcuts import redirect,render
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("users/", include("Users.urls")),
    path('App/',include("App.urls")), 
    path('',views.home,name="home"),
    path('contact/', views.contact, name='contact'), 
    path('about/', lambda request: render(request, 'about.html'), name='about'),
    path('subscribe-newsletter/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('ajax/increment-view/<int:pk>/',views.increment_post_view, name='increment_post_view'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)