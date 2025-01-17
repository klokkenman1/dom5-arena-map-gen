import os
import sys

from django.utils.translation import ugettext_lazy as _

import environ
import sentry_sdk
from corsheaders.defaults import default_headers
from sentry_sdk.integrations.django import DjangoIntegration

########################################################################################
#                                                                                      #
#                                                                                      #
#                                                   DJANGO SETTINGS                    #
#                                                                                      #
#   For more information on this file, see                                             #
#   https://docs.djangoproject.com/en/2.2/topics/settings/                             #
#                                                                                      #
#   For the full list of settings and their values, see                                #
#   https://docs.djangoproject.com/en/2.2/ref/settings/                                #
#                                                                                      #
#                                                                                      #
#                   - Environment specifics                                            #
#                   - Django basics                                                    #
#                   - Installed Apps & Middleware                                      #
#                   - Logging                                                          #
#                   - Databases                                                        #
#                   - Caching & RQ                                                     #
#                   - Static files                                                     #
#                   - API                                                              #
#                   - Security                                                         #
#                   - Testing                                                          #
#                   - App specific                                                     #
#                                                                                      #
#                                                                                      #
########################################################################################

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# .env file handling and some logic to ignore warnings about it not
# being found on production
env = environ.Env()
environ.Env.read_env(env_file=os.path.join(BASE_DIR, ".env"))

# Fail hard, every environment needs to set the stage
ENV = env.str("ENV")

# Set important directories

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

########################################################################################
#                                                                                      #
#                                            Django basics                             #
#                                                                                      #
########################################################################################

DEBUG = env.bool("DJANGO_DEBUG", False)
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# To make things easy for new developers, we are starting with a SECRET_KEY - we are
# checking this on production
SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="notsafeforproduction")

# Should have "*" for local, the site URL for production
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])
USE_X_FORWARDED_HOST = env.bool("USE_X_FORWARDED_HOST", default=False)

if ENV == "production":
    if DEBUG:
        sys.stderr.write(
            "**** CAUTION: You are running in production with DEBUG=True ****"
        )
    if SECRET_KEY == "notsafeforproduction":
        sys.exit(
            "**** CAUTION: You are running in production with "
            "SECRET_KEY=notsafeforproduction ****"
        )
    if ALLOWED_HOSTS == "*":
        sys.stderr.write(
            "**** CAUTION: You are running in production with ALLOWED_HOSTS=* ****"
        )


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en"
LANGUAGES = [("en", _("English"))]
USE_THOUSAND_SEPARATOR = True
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

ROOT_URLCONF = "conf.urls"

APPEND_SLASH = True

SITE_ID = 1

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            str(os.path.join(BASE_DIR, "templates")),
            os.path.join(BASE_DIR, "frontend/build"),
            os.path.join(BASE_DIR, "frontend/public"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "string_if_invalid": "{%s is missing}",
            "debug": DEBUG,
        },
        "NAME": "django",
    }
]

WSGI_APPLICATION = "conf.wsgi.application"

AUTH_USER_MODEL = "users.User"
ADMIN_URL = "admin/"
########################################################################################
#                                                                                      #
#                            Installed apps + Middleware                               #
#                                                                                      #
########################################################################################


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.redirects",
    "django.contrib.postgres",
    "corsheaders",
    "django_extensions",
    "rest_framework",
    "apps.core",
    "apps.domdata",
    "apps.users",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

########################################################################################
#                                                                                      #
#                                           Logging                                    #
#                                                                                      #
########################################################################################

SENTRY_DSN = env.str("SENTRY_DSN", default="")
if SENTRY_DSN:
    print("Sentry logging configured!")
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        # The traces_sample_rate can range from 0 to 1, inclusive.
        # To send 20% of transactions you need to set this value to 0.2.
        # Value 1 would be good for testing but you should change it on production mode.
        traces_sample_rate=env.float("TRACES_SAMPLE_RATE", default=0.2),
        send_default_pii=env.bool("SEND_DEFAUL_PPI", default=True),
    )

########################################################################################
#                                                                                      #
#                                          Databases                                  #
#                                                                                      #
########################################################################################

DATABASE_URL = env.str("DATABASE_URL", default="No")
DATABASES = {"default": env.db("DATABASE_URL")}

########################################################################################
#                                                                                      #
#                                      DJANGO REST                                     #
#                                                                                      #
########################################################################################
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
}


########################################################################################
#                                                                                      #
#                                           CORS                                       #
#                                                                                      #
########################################################################################
CORS_ORIGIN_ALLOW_ALL = env.bool("CORS_ORIGIN_ALLOW_ALL", default=False)

CORS_ORIGIN_WHITELIST = CSRF_TRUSTED_ORIGINS = env.list(
    "CORS_ORIGIN_WHITELIST", default=[]
)

CORS_ALLOW_CREDENTIALS = env.bool("CORS_ALLOW_CREDENTIALS", default=True)

CORS_ALLOW_HEADERS = default_headers + (
    "If-None-Match",
    "Last-Modified",
    "Accept-Language",
    "If-Modified-Since",
    "Access-Control-Allow-Origin",
)

CORS_EXPOSE_HEADERS = (
    "ETag",
    "Last-Modified",
    "HTTP_X_RESPONSE_ID",
    "HTTP_GIT_BRANCH",
    "Access-Control-Expose-Headers",
)
########################################################################################
#                                                                                      #
#                                           Silk                                       #
#                                                                                      #
########################################################################################
SILKY_PROFILER = env.bool("SILKY_PROFILER", False)

if SILKY_PROFILER:

    # Do not use potentially insecure and unnecessary apps in production
    INSTALLED_APPS += ["silk"]

    MIDDLEWARE = MIDDLEWARE + ["silk.middleware.SilkyMiddleware"]

    SILKY_META = env.bool("SILKY_META", False)  # Log time required for Silky profiling

########################################################################################
#                                                                                      #
#                                           Static files                               #
#                                                                                      #
########################################################################################

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Media
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "frontend/build/static"),
]


########################################################################################
#                                                                                      #
#                                           API                                        #
#                                                                                      #
########################################################################################

########################################################################################
#                                                                                      #
#                                           Security                                   #
#                                                                                      #
########################################################################################


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
        "OPTIONS": {
            "max_similarity": 0.7,
            "user_attributes": ("username", "first_name", "last_name", "email"),
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
]

if ENV == "production":
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
    SECURE_REDIRECT_EXEMPT = env.list("SECURE_REDIRECT_EXEMPT", default=["ht/"])

    # In order to detect when a request is made via SSL in Django
    # (for use in request.is_secure())
    # https://devcenter.heroku.com/articles/http-routing#heroku-headers
    SECURE_PROXY_SSL_HEADER = (
        env.str("SECURE_PROXY_SSL_HEADER", default="x-forwarded-proto"),
        "https",
    )

    # https://docs.djangoproject.com/en/1.10/ref/settings/#std:setting-SESSION_COOKIE_SECURE
    SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=True)

    # https://docs.djangoproject.com/en/1.10/ref/settings/#session-cookie-httponly
    CSRF_COOKIE_HTTPONLY = env.bool("CSRF_COOKIE_HTTPONLY", default=True)
    # https://docs.djangoproject.com/en/1.10/ref/settings/#csrf-cookie-secure
    CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=True)

    # https://docs.djangoproject.com/en/2.2/ref/middleware/#http-strict-transport-security
    HSTS_ENABLED = env.bool("SESSION_COOKIE_SECURE", default=True)
    if HSTS_ENABLED:
        SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31_536_000)
        SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
            "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True
        )
        SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=True)

    # https://docs.djangoproject.com/en/2.2/ref/clickjacking/
    X_FRAME_MIDDLEWARE_ENABLED = env.bool("X_FRAME_MIDDLEWARE_ENABLED", default=False)
    if X_FRAME_MIDDLEWARE_ENABLED:
        MIDDLEWARE = MIDDLEWARE + [
            "django.middleware.clickjacking.XFrameOptionsMiddleware"
        ]
        X_FRAME_OPTIONS = env.str("X_FRAME_OPTIONS", default="DENY")
    # https://docs.djangoproject.com/en/2.2/ref/middleware/#x-content-type-options-nosniff
    SECURE_CONTENT_TYPE_NOSNIFF = env.bool("SECURE_CONTENT_TYPE_NOSNIFF", default=False)
########################################################################################
#                                                                                      #
#                                           Testing                                    #
#                                                                                      #
########################################################################################


# RUNNING_TESTS should used really rarely because we want the CI to test
# the real production setup
if ENV == "test":

    # Django uses strong hashing algorithms, these are not needed in testing,
    # this speeds up things
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

    # Disabling debugging speeds up things
    DEBUG = False
    TEMPLATE_DEBUG = False

    # No SSL in testing
    DEFAULT_PROTOCOL = "http"

    import tempfile

    _temp_media = tempfile.mkdtemp()
    MEDIA_ROOT = _temp_media
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"


########################################################################################
#                                                                                      #
#                                           App specific                               #
#                                                                                      #
########################################################################################
