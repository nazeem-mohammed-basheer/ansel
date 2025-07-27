# bodhini_backend/accounts/urls.py

from django.urls import path
from . import views # Your accounts app views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Basic HTML Views
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),

    # Events URLs (New)
    path('events/', views.event_list, name='events'), # Display all categorized events
    path('events/<slug:slug>/', views.event_detail, name='event_detail'), # Individual event details

    # User authentication URLs
    path('login-register/', views.login_register_page_view, name='login_register'), # Combined login/register
    path('login/', auth_views.LoginView.as_view(template_name='login_register.html'), name='login'),

    # Password reset URLs (standard Django auth views)
    path('password_reset/',
          auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'),
          name='password_reset'),
    path('password_reset/done/',
          auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
          name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
          auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
          name='password_reset_confirm'),
    path('reset/done/',
          auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
          name='password_reset_complete'),

    # User profile and edit URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),

    # Logout view
    # Using next_page directly, as settings import is not ideal in urls.py
    path('logout/', auth_views.LogoutView.as_view(next_page='/accounts/login-register/'), name='logout'),
]