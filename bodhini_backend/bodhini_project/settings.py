import os
import sys

# BASE_DIR is the path to the inner 'bodhini_project' folder.
# Example: C:\Users\Nazeem M Basheer\ansel\bodhini_backend\bodhini_project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# PROJECT_ROOT should point to the 'bodhini_backend' folder,
# which is the parent directory of BASE_DIR.
# Example: C:\Users\Nazeem M Basheer\ansel\bodhini_backend
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'u184wm2v95' # IMPORTANT: Replace with a strong, unique key in production!

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# ...existing code...
ALLOWED_HOSTS = [
    'bodhini-gve6.onrender.com',
    'bodhini-2ndn.onrender.com',
    'localhost',
    '127.0.0.1'
]
# ...existing code...

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', # Essential for static files

    # Third-party apps
    'rest_framework',
    'rest_framework.authtoken', # Required for Token Authentication
    'corsheaders',              # Required for handling CORS requests from frontend
    

    # Your apps
    'bodhini_project',
    'media_manager',            # Ensure your app is here
    'accounts.apps.AccountsConfig', # Add your accounts app's AppConfig (recommended)
     
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # Must be placed high, preferably after SecurityMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bodhini_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_ROOT, 'templates')], # <--- CHANGE THIS LINE
                                                           # Use PROJECT_ROOT here!
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bodhini_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'db.sqlite3'), # Use PROJECT_ROOT for db.sqlite3
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# --- Custom Authentication Settings (CRITICAL for your requirements) ---
LOGIN_URL = '/accounts/login-register/' # This should point to your login/register page URL
LOGIN_REDIRECT_URL = '/' # After successful login, redirect to the home page (index.html)
LOGOUT_REDIRECT_URL = '/accounts/login-register/' # After logout, redirect back to login/register

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend', # Default Django authentication
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata' # Set to your local time zone (changed from UTC for consistency)

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/' # The URL prefix for static files

# This tells Django where to *find* your static files during development
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, 'static'), # Points to your 'bodhini_backend/static/' folder
]
# STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles') # Uncomment and run collectstatic for production deployment


# Media files (for user uploads like profile pictures)
MEDIA_URL = '/media/'
# MEDIA_ROOT is the absolute path to the directory where user-uploaded files are stored.
# This should be 'bodhini_backend/media/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media') # Use PROJECT_ROOT

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication', # For API authentication
        'rest_framework.authentication.SessionAuthentication', # For browsable API and Django's session-based auth
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated', # Require authentication for all API endpoints by default
    ]
}

# CORS Headers settings (for frontend communication)
CORS_ALLOW_ALL_ORIGINS = True # WARNING: For development only. Be specific in production!
CORS_ALLOWED_ORIGINS = [
     "http://localhost:8000", # Example if your frontend is served by a different local server
     "http://127.0.0.1:8000",
     #"file://", # Allow local file system access (useful for direct HTML file opening, but can be security risk)
]
CORS_ALLOW_CREDENTIALS = True # If you need to send cookies/auth headers with cross-origin requests

# Email Configuration for password reset etc.
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com' # Example for Gmail
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'nazeemmohammedbasheer@gmail.com' # IMPORTANT: Your email address
EMAIL_HOST_PASSWORD = 'rwmtoyupepoenvic' # IMPORTANT: Your email password or app password

# The email address that will appear as the sender in the recipient's inbox
DEFAULT_FROM_EMAIL = 'BODHINI Contact <noreply@bodhini.com>'

# The email address where you want to receive contact form messages
RECEIVING_EMAIL_ADDRESS = 'anvbasheer@gmail.com'
