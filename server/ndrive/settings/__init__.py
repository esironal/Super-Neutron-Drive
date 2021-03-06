# Django settings for myproject project.

import os
import logging
from logging.handlers import RotatingFileHandler

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DIR = os.path.normpath(os.path.dirname(BASE_DIR))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
  # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
    'NAME': 'sndrive',                      # Or path to database file if using sqlite3.
    'USER': 'postgres',
    'PASSWORD': '',
    'HOST': 'localhost',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
    'PORT': '5432',                      # Set to empty string for default.
  }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
  'super.neutrondrive.com',
  'snd.neutrondrive.com',
]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

STATIC_ROOT = '/var/www/html/static/'
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
  # Put strings here, like "/home/html/static" or "C:/www/django/static".
  # Always use forward slashes, even on Windows.
  # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
  'django.contrib.staticfiles.finders.FileSystemFinder',
  'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
  'django.template.loaders.filesystem.Loader',
  'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
  'ndrive.middleware.Secure',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.common.CommonMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  #'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'ndrive.urls'

WSGI_APPLICATION = 'ndrive.wsgi.application'

TEMPLATE_DIRS = ()

TEMPLATE_CONTEXT_PROCESSORS = (
  "django.contrib.auth.context_processors.auth",
  "django.core.context_processors.debug",
  #"django.core.context_processors.i18n",
  "django.core.context_processors.media",
  "django.core.context_processors.static",
  "django.core.context_processors.tz",
  "django.contrib.messages.context_processors.messages",
  "django.core.context_processors.request",
  "ndrive.context.site_context",
)

CACHES = {
  'default': {
    'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
    'LOCATION': '127.0.0.1:11211',
  }
}

INSTALLED_APPS = (
  'grappelli',
  
  'django.contrib.admin',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.messages',
  'django.contrib.staticfiles',
  
  'paypal.standard.ipn',
  
  'ndrive',
  'account',
  'editor',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'filters': {
    'require_debug_false': {
      '()': 'django.utils.log.RequireDebugFalse'
    }
  },
  'handlers': {
    'mail_admins': {
      'level': 'ERROR',
      'filters': ['require_debug_false'],
      'class': 'django.utils.log.AdminEmailHandler'
    }
  },
  'loggers': {
    'django.request': {
      'handlers': ['mail_admins'],
      'level': 'ERROR',
      'propagate': True,
    },
  }
}

LOGS_DIR = os.path.join(os.path.dirname(BASE_DIR), 'logs')
if not os.path.exists(LOGS_DIR):
  os.makedirs(LOGS_DIR)
  
JS_ERROR_LOGGER = logging.getLogger("JS_ERROR_LOGGER")
JS_ERROR_LOGGER.setLevel(logging.INFO)
JS_LOG = os.path.join(LOGS_DIR, 'js-errors.log')

formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')
handler = RotatingFileHandler(JS_LOG, maxBytes=1024 * 1024, backupCount=9)
handler.setFormatter(formatter)

JS_ERROR_LOGGER.addHandler(handler)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

AUTH_USER_MODEL = 'account.User'

SITE_NAME = 'Neutron Drive'

GRAPPELLI_ADMIN_HEADLINE = 'Neutron Drive'
GRAPPELLI_ADMIN_TITLE = 'Neutron Drive Admin'

SESSION_COOKIE_NAME = 'snd-sessionid'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = False
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

DEV = False

import sys
import socket

machine = socket.gethostname().split('.')[0]

try:
  istr = 'ndrive.settings.private.' + machine
  tmp = __import__(istr)
  mod = sys.modules[istr]

except ImportError:
  print 'No settings module for %s' % machine

else:
  print 'Importing settings for %s' % machine
  for setting in dir(mod):
    if setting == setting.upper():
      setattr(sys.modules[__name__], setting, getattr(mod, setting))
      
