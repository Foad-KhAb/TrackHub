import os

STAGING_ENV = "staging"
PRODUCTION_ENV = "production"
DEVELOPMENT_ENV = "development"
ENVIRONMENT = os.environ.get("ENV", DEVELOPMENT_ENV).lower()

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",

    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",

    "accounts",
    "orgs",
]

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "1000/min",
        "user": "1000/min",
    },
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

ROOT_URLCONF = "_base.urls"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "TrackHub",
        "USER": "postgres",
        "PASSWORD": "yourStrongPassword",
        "HOST": "localhost",
        "PORT": 5432,
    }
}
AUTH_PASSWORD_VALIDATORS = [
    # Avoid passwords similar to user info
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        "OPTIONS": {
            "user_attributes": ("username", "email", "first_name", "last_name"),
            "max_similarity": 0.7,
        },
    },

    # Length (bump to 14 for better baseline)
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 14},
    },

    # Block common passwords (optionally use your own list)
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },

    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},

    {"NAME": "utils.password_validators.UppercaseValidator"},
    {"NAME": "utils.password_validators.LowercaseValidator"},

    {"NAME": "utils.password_validators.DigitValidator"},         # at least 1 digit
    {"NAME": "utils.password_validators.SymbolValidator"},        # at least 1 symbol
    {"NAME": "utils.password_validators.NoWhitespaceValidator"},  # no spaces/tabs/newlines
]

REDIS_URL_DEFAULT = os.getenv("REDIS_URL_DEFAULT", "redis://127.0.0.1:6379/0")
REDIS_URL_FETCH   = os.getenv("REDIS_URL_FETCH",   "redis://127.0.0.1:6379/1")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL_DEFAULT,
        "KEY_PREFIX": os.getenv("CACHE_KEY_PREFIX", "myapp"),  # avoids key collisions across envs
        "TIMEOUT": int(os.getenv("CACHE_DEFAULT_TIMEOUT", 60 * 10)),  # 10 minutes
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PARSER_CLASS": "redis.connection.HiredisParser",  # faster parsing if hiredis installed
            "CONNECTION_POOL_KWARGS": {
                "max_connections": int(os.getenv("REDIS_MAX_CONN", 100)),
            },
            "SOCKET_CONNECT_TIMEOUT": float(os.getenv("REDIS_CONNECT_TIMEOUT", 2.0)),
            "SOCKET_TIMEOUT": float(os.getenv("REDIS_SOCKET_TIMEOUT", 2.0)),
            "RETRY_ON_TIMEOUT": True,
            "IGNORE_EXCEPTIONS": True,  # behave like memcached: if Redis is down, fail softly
            # Optional: compress large values to save memory/bandwidth
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            # Optional: custom serializer (json is portable; pickles are fastest but opaque)
            # "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
        },
    },

    # Separate alias for data fetched from external APIs, with different TTL
    "fetch": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL_FETCH,
        "KEY_PREFIX": os.getenv("FETCH_CACHE_KEY_PREFIX", "myapp:fetch"),
        "TIMEOUT": int(os.getenv("FETCH_CACHE_TIMEOUT", 60 * 5)),  # 5 minutes
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PARSER_CLASS": "redis.connection.HiredisParser",
            "CONNECTION_POOL_KWARGS": {"max_connections": int(os.getenv("REDIS_MAX_CONN", 100))},
            "SOCKET_CONNECT_TIMEOUT": float(os.getenv("REDIS_CONNECT_TIMEOUT", 2.0)),
            "SOCKET_TIMEOUT": float(os.getenv("REDIS_SOCKET_TIMEOUT", 2.0)),
            "RETRY_ON_TIMEOUT": True,
            "IGNORE_EXCEPTIONS": True,
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
        },
    },
}

from datetime import timedelta

SIMPLE_JWT = {
    # How long access tokens live (short-lived for security)
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),

    # How long refresh tokens live
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    # Rotate refresh tokens on every use
    "ROTATE_REFRESH_TOKENS": True,

    # Blacklist used refresh tokens (needs rest_framework_simplejwt.token_blacklist in INSTALLED_APPS)
    "BLACKLIST_AFTER_ROTATION": True,

    # Token signing algorithm and secret
    "ALGORITHM": "HS256",
    "SIGNING_KEY": "SECRET_KEY",   # usually your Django SECRET_KEY

    # Prefix in the HTTP Authorization header → "Authorization: Bearer <token>"
    "AUTH_HEADER_TYPES": ("Bearer",),

    # Options for token claims
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",

    # Sliding token config (optional, only if you use sliding tokens)
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=15),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=7),
}
AUTH_USER_MODEL = "users.Member"