# bodhini_backend/media_manager/admin.py

from django.contrib import admin
from .models import Media # Assuming you have a Media model in media_manager/models.py
from accounts.models import Event # CORRECT: Import Event from accounts.models

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_type', 'uploaded_at')
    list_filter = ('media_type',)
    search_fields = ('title', 'description')
    date_hierarchy = 'uploaded_at'

# Register Event model with its custom admin options
@admin.register(Event) # This decorator registers the Event model
class EventAdmin(admin.ModelAdmin):
    # These display columns in the admin list view
    # CRUCIAL FIX: Use 'admin_get_status' which is the method with the @admin.display decorator
    list_display = ('title', 'start_datetime', 'duration_hours', 'is_active', 'admin_get_status')
    # These create filter options on the right sidebar
    list_filter = ('is_active', 'start_datetime')
    # These enable searching
    search_fields = ('title', 'main_speaker')
    # Automatically generate slug from title
    prepopulated_fields = {'slug': ('title',)}

    # Define the fields that appear in the add/change form for an Event object
    fields = (
        'title',
        'slug',
        'about_event',      # Matches the field name in accounts/models.py
        'main_speaker',
        'start_datetime',
        'duration_hours',   # <--- This makes the field visible and editable
        'event_image',
        'registration_link',
        'is_active',
    )
    # Optional: date_hierarchy is used for drilling down by date on the list view
    date_hierarchy = 'start_datetime'