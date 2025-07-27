import os
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
import time

register = template.Library()

@register.filter
def cachebust(file_field):
    # If file_field is None or an empty string, return empty
    if not file_field:
        print("DEBUG: cachebust filter: Input file_field is empty (None or empty string). Returning empty.")
        return ""

    # If file_field is an actual FileField/ImageField object (has .path and .url attributes)
    if hasattr(file_field, 'path') and hasattr(file_field, 'url'):
        try:
            file_path = file_field.path
            timestamp = int(os.path.getmtime(file_path))
            original_url = file_field.url
            new_url = f"{original_url}?v={timestamp}"
            print(f"DEBUG: cachebust filter (File Object): Original URL={original_url}, Timestamp={timestamp}, New URL={new_url}")
            return mark_safe(new_url)
        except FileNotFoundError:
            print(f"DEBUG: cachebust filter (File Object): File not found for {file_field.url}. Returning original URL without cachebust.")
            return mark_safe(file_field.url)
        except Exception as e:
            print(f"DEBUG: cachebust filter error (File Object): {e}. Returning original URL {file_field.url}")
            return mark_safe(file_field.url)
    # If file_field is a string, it means it's likely an already-constructed URL from Django's .url
    # or a default string from the model (like 'default.jpg' if it still had that default).
    elif isinstance(file_field, str):
        original_url = file_field # It's already the URL, or a relative path from MEDIA_URL
        
        # If the string does NOT start with MEDIA_URL, prepend it.
        # This covers cases like 'default.jpg' if you bring that default back.
        # But if it's already a full URL like /media/profile_pics/..., don't prepend.
        if not original_url.startswith(settings.MEDIA_URL) and not original_url.startswith('/static/'):
             original_url = settings.MEDIA_URL + original_url

        # We cannot apply cachebust if it's just a string path that might not exist on disk
        # (e.g., if it's a default that points to a non-physical file)
        # However, if it IS a physical file, we can try to get its timestamp.
        # But for simplicity, if it's a string, we'll return it as is, or with a basic timestamp for consistency if it's a media URL.
        
        # Simpler approach: If it's a string, just return it as is.
        # The primary use case for cachebust is actual uploaded FileField objects.
        print(f"DEBUG: cachebust filter (String Input): Input was string: '{file_field}'. Returning as is or with prepended MEDIA_URL if needed: {original_url}. No dynamic cachebust.")
        return mark_safe(original_url)
    else:
        # Fallback for any other unexpected type
        print(f"DEBUG: cachebust filter: Unexpected type for file_field: {type(file_field)}. Returning empty string.")
        return ""