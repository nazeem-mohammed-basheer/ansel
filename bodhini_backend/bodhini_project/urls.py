# bodhini_backend/bodhini_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import os # Make sure os is imported for path.join

from accounts import views as accounts_views # For register_view, contact_view, and now home, about, services, events_list
from rest_framework.authtoken import views as authtoken_views

# AuthenticatedTemplateView is no longer needed here as we are using specific views
# from accounts.views for the main pages.
# from .views import AuthenticatedTemplateView # REMOVED

urlpatterns = [
    path('admin/', admin.site.urls),

    # API Authentication URLs (Accessible for API clients)
    path('api/auth/', include([
        path('token/', authtoken_views.obtain_auth_token, name='api_token_auth'),
        path('register/', accounts_views.register_view, name='api_register'), # Your API register view
    ])),

    # Accounts App URLs (for HTML Pages) - all prefixed with /accounts/
    # This include handles login/register, profile, edit profile, password reset,
    # and also the specific /accounts/events/ and /accounts/events/<slug>/ if defined there.
    path('accounts/', include('accounts.urls')),

    # MAIN SITE CONTENT URLs - now using specific views from accounts.views
    # These views handle their own authentication redirection if needed (e.g., @login_required)
    path('', accounts_views.home, name='home'),
    path('about/', accounts_views.about, name='about'),
    path('services/', accounts_views.services, name='service'), # CORRECTED: path is now 'services/'
    path('events/', accounts_views.event_list, name='events'), # Using the event_list view from accounts app

    # Contact page - directly using accounts_views.contact_view
    path('contact/', accounts_views.contact, name='contact'), # Corrected: using accounts_views.contact

    # Other API URLs (e.g., from media_manager app)
    path('api/media/', include('media_manager.urls')),
]

# Serve static and media files only during development (DEBUG=True)
if settings.DEBUG:
    # Serve media files (user uploads)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Serve static files (CSS, JS, images from static folder)
    # This line ensures it's explicitly served.
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.PROJECT_ROOT, 'static'))