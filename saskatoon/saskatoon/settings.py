import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv #type: ignore

# SECURITY WARNING: keep the secret key used in production secret!
# More infos: https://docs.djangoproject.com/fr/3.1/ref/settings/#secret-key
SECRET_KEY='u0f_#j5dclpq0*--ixv61j1j$!@0t(!62z+(o&*@u7_gf&n#_@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG='yes'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'saskatoon_prod',
        'USER': 'saskatoon',
        'PASSWORD': 'saskatoon',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'u0f_#j5dclpq0*--ixv61j1j$!@0t(!62z+(o&*@u7_gf&n#_@'

# SECURITY WARNING: don't run with debug turned on in production!
if os.getenv('SASKATOON_DEBUG') is not None:
    DEBUG = os.getenv('SASKATOON_DEBUG', '').lower() in ['yes', 'true'] 
else:
    DEBUG = False

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ckeditor',
    'leaflet',
    'sitebase',
    'member',
    'harvest',
    'rest_framework',
    'django_filters',
    'crispy_forms',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'saskatoon.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'saskatoon.wsgi.application'



# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('fr',u'Français'),
    ('en',u'English'),
]

LOCALE_PATHS = [
    'harvest/locale/',
    'member/locale/',
    'sitebase/locale/',
    'saskatoon/locale/'
]

CSRF_COOKIE_SECURE = True

TIME_ZONE = os.getenv('SASKATOON_TIME_ZONE') or 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

# CUSTOM STUFF

AUTH_USER_MODEL = "member.AuthUser"

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
   'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
   'PAGINATE_BY': 10,
   'DEFAULT_RENDERER_CLASSES': (
   'rest_framework.renderers.TemplateHTMLRenderer',
   'rest_framework.renderers.JSONRenderer',
)
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

CRISPY_TEMPLATE_PACK = 'bootstrap4'

