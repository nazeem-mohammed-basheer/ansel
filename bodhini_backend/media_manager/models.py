# media_manager/models.py

from django.db import models

class Media(models.Model):
    MEDIA_TYPES = [
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('image', 'Image'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    file = models.FileField(upload_to='uploaded_media/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Media Resources"
        ordering = ['-uploaded_at']

# New: Event Model
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_date = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, null=True)
    registration_link = models.URLField(max_length=500, blank=True, null=True)
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Events"
        ordering = ['event_date'] # Order by upcoming events
