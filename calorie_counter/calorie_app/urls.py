from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_food, name='search_food'),
    path('add/', views.add_to_log, name='add_to_log'),
    path('log/', views.daily_log, name='daily_log'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]