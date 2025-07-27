# media_manager/urls.py

from django.urls import path
from .views import MediaListCreateView, MediaRetrieveUpdateDestroyView, ContactFormView, EventListView, EventCreateView # Import EventCreateView

urlpatterns = [
    path('', MediaListCreateView.as_view(), name='media-list-create'),
    path('<int:pk>/', MediaRetrieveUpdateDestroyView.as_view(), name='media-detail'),
    path('submit-contact/', ContactFormView.as_view(), name='submit-contact'),

    # Events URLs
    path('events/', EventListView.as_view(), name='event-list'),
    path('events/create/', EventCreateView.as_view(), name='event-create'), # NEW: Event creation endpoint
]
