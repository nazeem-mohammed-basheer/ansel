from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib import messages
from django.utils import timezone # Import timezone for events logic

# Import for making HTTP requests to the email validator API
import requests
import json # For handling JSON data

# Import all necessary forms and models
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, ContactForm
from .models import Profile, Event # <--- IMPORTED Event model

# Define the URL for your email validator API
# IMPORTANT: Replace with the actual URL where your Flask app is running
EMAIL_VALIDATOR_API_URL = "http://127.0.0.1:5000/validate-email"

# API View for user registration (for AJAX/frontend API calls)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    password2 = request.data.get('password2')

    if not all([username, email, password, password2]):
        messages.error(request, 'All fields are required for registration.')
        return Response({'detail': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if password != password2:
        messages.error(request, 'Passwords do not match.')
        return Response({'password': ['Passwords do not match.']}, status=status.HTTP_400_BAD_REQUEST)

    # --- Start Email Validation API Call ---
    try:
        # Prepare the data to send to the email validator API
        payload = {"email": email}
        headers = {"Content-Type": "application/json"}

        # Make a POST request to the email validator API
        response = requests.post(EMAIL_VALIDATOR_API_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        # Parse the JSON response from the validator API
        validation_result = response.json()

        # Check the 'is_valid' flag from the API response
        if not validation_result.get('is_valid'):
            error_message = validation_result.get('message', 'Email format is invalid.')
            messages.error(request, error_message) # This message is set for Django's messages framework
            # Return a 400 response with the error message in the JSON payload
            # The frontend JavaScript should read this JSON response to display the error.
            return Response({'email': [error_message]}, status=status.HTTP_400_BAD_REQUEST)

    except requests.exceptions.ConnectionError:
        # Handle cases where the validator API is not reachable
        messages.error(request, 'Could not connect to the email validation service. Please try again later.')
        return Response({'detail': 'Email validation service unavailable.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except requests.exceptions.Timeout:
        # Handle cases where the validator API takes too long to respond
        messages.error(request, 'Email validation service timed out. Please try again later.')
        return Response({'detail': 'Email validation service timed out.'}, status=status.HTTP_504_GATEWAY_TIMEOUT)
    except requests.exceptions.RequestException as e:
        # Catch any other request-related errors
        messages.error(request, f'An error occurred during email validation: {e}')
        return Response({'detail': f'Email validation failed: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # --- End Email Validation API Call ---

    if User.objects.filter(username=username).exists():
        messages.error(request, 'A user with that username already exists.')
        return Response({'username': ['A user with that username already exists.']}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email=email).exists():
        messages.error(request, 'A user with that email already exists.')
        return Response({'email': ['A user with that email already exists.']}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Registration successful! Please log in.')
        return Response({'message': 'User registered successfully!'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        messages.error(request, f'Registration failed: {e}')
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# HTML View to display the login/registration page
def login_register_page_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'login_register.html')

# Basic HTML Views (Home, About, Services, Contact)
def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'service.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            messages.success(request, 'Your message has been sent successfully!') # Fallback success message
            return render(request, 'contact.html', {'form': form}) # Or redirect
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else: # GET request
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

# New: Events List View
def event_list(request):
    now = timezone.now()
    all_events = Event.objects.filter(is_active=True).order_by('start_datetime')

    ongoing_events = []
    upcoming_events = []
    previous_events = []

    for event in all_events:
        status = event.get_status()
        if status == 'ongoing':
            ongoing_events.append(event)
        elif status == 'upcoming':
            upcoming_events.append(event)
        else: # previous
            previous_events.append(event)

    context = {
        'ongoing_events': ongoing_events,
        'upcoming_events': upcoming_events,
        'previous_events': previous_events,
    }
    return render(request, 'events.html', context)

# New: Event Detail View
def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug, is_active=True)
    context = {
        'event': event
    }
    return render(request, 'event_detail.html', context)

# User Profile View (HTML)
@login_required
def profile_view(request):
    # Ensure a Profile exists for the user. This handles cases where a user might be created
    # without the post_save signal immediately triggering (e.g., via Django admin directly).
    if not hasattr(request.user, 'profile') or request.user.profile is None:
        Profile.objects.create(user=request.user)
    return render(request, 'profile.html')

# Edit Profile View (HTML)
@login_required
def edit_profile_view(request):
    """
    Handles updating the user's personal information (User model) and profile details (Profile model).
    """
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else: # GET request
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    # Removed old debugging print statements for template search paths
    return render(request, 'edit_profile.html', context)
def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug)

    # Determine if registration is still open
    current_status = event.get_status() # Use the method from the model
    # Registration is allowed only if the event is 'upcoming' or 'ongoing'
    # You might even restrict it to just 'upcoming' if you want registration to close AT start.
    registration_open = current_status in ['upcoming', 'ongoing']

    context = {
        'event': event,
        'registration_open': registration_open, # Pass this flag to the template
    }
    return render(request, 'event_detail.html', context)

# ... event_list view (as it is) ...
def event_list(request):
    all_events = Event.objects.filter(is_active=True).order_by('start_datetime')
    now = timezone.now()

    # Apply the get_status logic to categorize events
    ongoing_events = []
    upcoming_events = []
    previous_events = []

    for event in all_events:
        status = event.get_status()
        if status == 'ongoing':
            ongoing_events.append(event)
        elif status == 'upcoming':
            upcoming_events.append(event)
        else: # status == 'previous'
            previous_events.append(event)

    context = {
        'ongoing_events': ongoing_events,
        'upcoming_events': upcoming_events,
        'previous_events': previous_events,
    }
    return render(request, 'events.html', context)
