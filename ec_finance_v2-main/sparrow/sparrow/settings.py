import os

import environ

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = ["*"]

# MACHINE SPECIFIC CHANGES
MEDIA_ROOT = env("MEDIA_ROOT")
RESOURCES_ROOT = env("RESOURCES_ROOT")
STATIC_ROOT = env("STATIC_ROOT")
TEMP_DATA = env("TEMP_DATA")
# END
MEDIA_URL = env("MEDIA_URL")
RESOURCES_URL = env("RESOURCES_URL")
STATIC_URL = env("STATIC_URL")
LOGIN_REDIRECT_URL = "/b/"
LOGIN_URL = "/accounts/signin/"

# impersonate credentials
FILE_SERVER_DOMAIN = env("FILE_SERVER_DOMAIN")
FILE_SERVER_USER = env("FILE_SERVER_USER")
FILE_SERVER_PWD = env("FILE_SERVER_PWD")
FILE_SERVER_PATH = env("FILE_SERVER_PATH")

# Application definition
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "post_office",
    "widget_tweaks",
    "base",
    "accounts",
    "auditlog",
    "mails",
    "messaging",
    "attachment",
    "exception_log",
    "task",
    "collection"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "stronghold.middleware.LoginRequiredMiddleware",
]

SILENCED_SYSTEM_CHECKS = [
    "admin.E408",
    "admin.E409",
    "admin.E410",
    "urls.E007",
]

ROOT_URLCONF = "sparrow.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
            ],
        },
    },
]

WSGI_APPLICATION = "sparrow.wsgi.application"

# DATABASES = {"default": {"ENGINE": env("ENGINE"), "NAME": env("NAME"), "USER": env("USER"), "PASSWORD": env("PASSWORD"), "HOST": env("HOST"), "PORT": env("PORT")}}

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": os.path.join(PROJECT_DIR, env("TESTDB"))}}


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

MAX_UPLOAD_SIZE = "5242880"


LOGGING = {
    "version": 1,
    "loggers": {"applog": {"handlers": ["logfile"], "level": "DEBUG"}},
    "handlers": {"logfile": {"level": "DEBUG", "class": "logging.FileHandler", "filename": "applog.log", "formatter": "simple"}},
    "formatters": {
        "simple": {"format": "[%(asctime)s] | %(levelname)s | %(message)s", "datefmt": "%Y-%m-%d %H:%M:%S"},
        "verbose": {"format": "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", "datefmt": "%Y-%m-%d %H:%M:%S"},
    },
}

# CELERY SETTINGS
BROKER_URL = env("BROKER_URL")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

REST_FRAMEWORK = {"DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination", "PAGE_SIZE": 10}


FARNELL_API_KEY = {}

AZURE_EXCE_ATTEMPT = 3

USE_TZ = False

AWS_S3_HANDLER = "https://sparrow-bg.s3.us-east-2.amazonaws.com/"


ASGI_APPLICATION = "sparrow.channel_asgi.application"

REDIS_HOST = "127.0.0.1"


AWS_ACCESS_KEY = env("AWS_ACCESS_KEY")
AWS_SECRET = env("AWS_SECRET")

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240
DEFAULT_COLOR_SCHEME = "bg_color:#042853,button_color:#042853,link_color:#1f1bc1,row_color:#e4e4e4,db_bg_color:#d5e3f4"
DEFAULT_PORTAL_COLOR_SCHEME = "bg_color:#042853,button_color:#042853,link_color:#1f1bc1,row_color:#e4e4e4,db_bg_color:#d5e3f4"

EC_PY_URL = env("EC_PY_URL")
EC_PORTAL_DOMAIN= env("EC_PORTAL_DOMAIN")

CLICK_UP_API = env("CLICK_UP_API")
