"""
Django settings for services project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'pjid#&u(2)bz@)8=5daqtt4+a&ym(q*f!vcxrjw(_9$+#y2poj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['.mayafin.in']

INTERNAL_IPS = ['127.0.0.1']

WEB_URL = 'https://mayafin.in'

SITE_URL = 'https//services.mayafin.in'

ADMINS = (
    ('MayaFin Admin', 'admin@mayafin.in'),
)

# Application definition

INSTALLED_APPS = [
    'material.admin',
    'material.admin.default',

    #'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework.authtoken',
    'rest_framework',
    'corsheaders',
    'drf_yasg2',

    'admin_reorder',
    'django_json_widget',

    'base',
    'platforms',
    'borrowers',
    'lenders',
    'API',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

MIDDLEWARE += ('django_structlog.middlewares.RequestMiddleware',)
MIDDLEWARE += ('admin_reorder.middleware.ModelAdminReorder',)

ROOT_URLCONF = 'services.urls'

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

WSGI_APPLICATION = 'services.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

ROOT = '/'
API = 'api/'
ADMIN = 'admin/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

API_URL = SITE_URL + ROOT + API
ADMIN_URL = SITE_URL + ROOT + ADMIN
LOGIN_REDIRECT_URL = ADMIN_URL
LOGIN_URL = LOGIN_REDIRECT_URL + 'login/'
LOGOUT_URL = LOGIN_REDIRECT_URL + 'logout/'


import structlog

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        },
        "plain_console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),
        },
        "key_value": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.KeyValueRenderer(key_order=['timestamp', 'level', 'event', 'logger']),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json_formatter",
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'json_formatter',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'API': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.ExceptionPrettyPrinter(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        #'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'EXCEPTION_HANDLER': 'API.views.exception_handler',
    'UPLOADED_FILES_USE_URL': True,
}


API_CONTACT = {
    "url": WEB_URL,
    "name": ADMINS[0][0],
    "email": ADMINS[0][1],
}


SWAGGER_SETTINGS = {
    "SPEC_URL": API_URL + 'swagger.yaml',
    'SECURITY_DEFINITIONS': {
        'Token': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        },
        'Session': {
            'type': 'basic',
        },
    },
    "DEFAULT_AUTO_SCHEMA_CLASS": "API.schema.AutoSchema",
}


REDOC_SETTINGS = {
    "SPEC_URL": API_URL + 'swagger.yaml',
    "REQUIRED_PROPS_FIRST": True,
    "TITLE": 'MayaFin Services API',
}


CORS_URLS_REGEX = r'^/api/.*$'

CORS_ALLOW_ALL_ORIGINS = True

CORS_ORIGIN_ALLOW_ALL = True


MATERIAL_ADMIN_SITE = {
    'HEADER':  ('MayaFin Services Admin'),  # Admin site header
    'TITLE':  ('MayaFin Services Admin'),  # Admin site title
    'FAVICON':  'API/images/favicon.ico',  # Admin site favicon (path to static should be specified)
    'MAIN_BG_COLOR':  '#2b5d83',  # Admin site main color, css color should be specified
    'MAIN_HOVER_COLOR':  '#2b5d83',  # Admin site main hover color, css color should be specified
    'PROFILE_PICTURE':  'material/admin/images/login-logo-default.jpg',  # Admin site profile picture (path to static should be specified)
    'LOGIN_LOGO':  'material/admin/images/login-logo-default.jpg',  # Admin site logo on login page (path to static should be specified)
    'PROFILE_BG':  'material/admin/images/login-bg-default.jpg',  # Admin site profile background (path to static should be specified)
    'LOGOUT_BG':  'material/admin/images/login-bg-default.jpg',  # Admin site background on login/logout pages (path to static should be specified)
    'SHOW_THEMES':  True,  #  Show default admin themes button
    'TRAY_REVERSE': True,  # Hide object-tools and additional-submit-line by default
    'NAVBAR_REVERSE': False,  # Hide side navbar by default
    'SHOW_COUNTS': False,
    'APP_ICONS': {
        'authtoken': 'vpn_key',
        'borrowers': 'person',
        'platforms': 'settings_system_daydream',
        'lenders': 'account_balance',
    },
    'MODEL_ICONS': {
        'tokenproxy': 'vpn_key',

        'loanapplication': 'account_box',
        'loanapplicationdata': 'perm_contact_calendar',

        'loanmanagementsystem': 'account_balance_wallet',
        'loanmanagementsystemapi': 'import_export',
        'channelpartners': 'touch_app',

        'loan': 'monetization_on',
        'lendersystem': 'account_balance',
        'lendersystemapi': 'import_export',
    },
}

ADMIN_REORDER = (
    {
        'app': 'borrowers',
        'models': (
            'borrowers.LoanApplication',
            'borrowers.LoanApplicationData',
        )
    },
    'API',
    {
        'app': 'platforms',
        'models': (
            'platforms.LoanManagementSystem',
            'platforms.LoanManagementSystemAPI',
            'platforms.ChannelPartners',
        )
    },
    {
        'app': 'lenders',
        'models': (
            'lenders.Loan',
            'lenders.LenderSystem',
            'lenders.LenderSystemAPI',
        )
    },
)



##################### END OF SETTINGS ################################
from django_settings_local import import_local;import_local(globals())
##################### END OF SETTINGS ################################
