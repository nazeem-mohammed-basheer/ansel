# media_manager/views.py

from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import send_mail
from django.conf import settings

from .models import Media, Event
from .serializers import MediaSerializer, ContactFormSerializer, EventSerializer
from .permissions import IsAdminUserOrReadOnly, IsAuthenticatedAndAdmin # NEW: Import custom permissions

# Existing Media API Views
class MediaListCreateView(generics.ListCreateAPIView):
    """
    API view to list all media items or create a new media item.
    GET requests (listing) are allowed for anyone (public).
    POST requests (creation) require admin (staff) authentication.
    """
    queryset = Media.objects.all().order_by('-uploaded_at')
    serializer_class = MediaSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method == 'GET':
            return [AllowAny()] # Allow anyone to list media
        # For POST (create), require admin (staff) user
        return [IsAuthenticatedAndAdmin()] # Changed to IsAuthenticatedAndAdmin

class MediaRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific media item.
    Only admin (staff) users can update/delete. Read-only for others.
    """
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAdminUserOrReadOnly] # Changed to IsAdminUserOrReadOnly
    lookup_field = 'pk'

# Contact Form Submission API View (remains unchanged)
class ContactFormView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ContactFormSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            email = serializer.validated_data['email']
            subject = serializer.validated_data.get('subject', '')
            message = serializer.validated_data['message']

            try:
                send_mail(
                    subject=f"BODHINI Contact Form: {subject} from {name}",
                    message=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.RECEIVING_EMAIL_ADDRESS],
                    fail_silently=False,
                )
                return Response({'message': 'Message sent successfully!'}, status=status.HTTP_200_OK)
            except Exception as e:
                print(f"Error sending email: {e}")
                return Response(
                    {'error': 'Failed to send message. Please try again later.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Event List API View (remains public for GET)
class EventListView(generics.ListAPIView):
    """
    API view to list all events.
    Allowed for anyone (public).
    """
    queryset = Event.objects.all().order_by('event_date') # Ensure ordering for upcoming events
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

# New: Event Creation API View (Admin only)
class EventCreateView(generics.CreateAPIView):
    """
    API view to create a new event.
    Requires admin (staff) authentication.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedAndAdmin] # Only admin (staff) users can create events
