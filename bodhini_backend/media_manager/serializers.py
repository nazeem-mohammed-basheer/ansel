# media_manager/serializers.py

from rest_framework import serializers
from .models import Media, Event # Import Event model

# Media Serializer (for your Media model)
class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'

# Contact Form Serializer (for handling contact form submissions)
class ContactFormSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=True)
    email = serializers.EmailField(required=True)
    subject = serializers.CharField(max_length=200, required=False, allow_blank=True)
    message = serializers.CharField(required=True)

    def validate_email(self, value):
        if "@" not in value:
            raise serializers.ValidationError("Invalid email format.")
        return value

# New: Event Serializer
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
