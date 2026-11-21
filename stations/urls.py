from django.urls import path
from django.contrib.auth import views as auth
from . import views
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('station/<int:pk>/', views.station, name='station'),
    path('station/<int:pk>/command/', views.send_command, name='command'),
    path('api/live/', views.live, name='live'),
    path('people/', views.people, name='people'),
    path('station/<int:pk>/export.csv', views.export, name='export'),
    path('supplies/', views.supplies, name='supplies'),
    path('incidents/', views.incidents, name='incidents'),
    path('login/', auth.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth.LogoutView.as_view(), name='logout'),
]
