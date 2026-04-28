# analytics/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.property_list, name='property_list'),
    path('add/', views.property_add, name='property_add'),
    path('<int:pk>/edit/', views.property_edit, name='property_edit'),
    path('<int:pk>/delete/', views.property_delete, name='property_delete'),
    path('report/', views.portfolio_report, name='portfolio_report'),
]