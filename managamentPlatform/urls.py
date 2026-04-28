"""
URL configuration for managamentPlatform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.views.generic import RedirectView #importing RedirectView to redirect the root URL

urlpatterns = [
    path("admin/", admin.site.urls),
    path('properties/', include('analytics.urls')), #connecting app urls to project urls
    # This line redirects the empty "" path to your properties list
    path('', RedirectView.as_view(url='properties/', permanent=True)),
]
