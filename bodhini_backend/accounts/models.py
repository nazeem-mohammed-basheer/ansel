# bodhini_backend/accounts/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib import admin # <--- ADDED: Import admin for @admin.display decorator

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Removed default='default.jpg'. Now, if no image is uploaded, this field will be truly empty (None).
    # The template will then fall back to the {% else %} block with static 'images/default_profile.png'.
    image = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'

# Signal to create a Profile for new Users when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# This signal is generally not needed and can cause infinite recursion issues.
# It's better to explicitly save the profile in your views (e.g., edit_profile_view)
# when the profile object is modified.
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()

# New Event Model
class Event(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200, help_text="A unique identifier for the event in the URL.")
    about_event = models.TextField() # This was previously 'description' in admin.py, ensure consistency
    main_speaker = models.CharField(max_length=100, blank=True, null=True)
    start_datetime = models.DateTimeField() # <--- CORRECTED: Removed duplicate definition
    duration_hours = models.DecimalField( # <--- CORRECTED: Removed duplicate definition
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Duration in hours (e.g., 2.5 for 2 hours 30 mins)"
    )
    event_image = models.ImageField(upload_to='event_pics', blank=True, null=True)
    registration_link = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True, help_text="Set to False to hide event without deleting.")

    class Meta:
        ordering = ['start_datetime'] # Order events by their start time

    def __str__(self):
        return self.title

    def get_status(self):
        now = timezone.now()
        # Calculate end_datetime only if duration_hours is not None
        # CRUCIAL FIX: Cast Decimal to float for timedelta hours component
        if self.duration_hours is not None:
            end_datetime = self.start_datetime + timezone.timedelta(hours=float(self.duration_hours))
        else:
            end_datetime = self.start_datetime # If no duration, it's considered instantaneous

        if now < self.start_datetime:
            return 'upcoming'
        elif self.start_datetime <= now <= end_datetime:
            return 'ongoing'
        else: # Event has ended
            return 'previous'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('event_detail', kwargs={'slug': self.slug})

    # Method for displaying status in Django admin list view
    @admin.display(description='Status') # <--- ADDED: Decorator for admin display
    def admin_get_status(self):
        return self.get_status()