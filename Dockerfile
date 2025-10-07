# =========================
# Stage 1 — build wheels
# =========================
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps needed to compile psycopg2 and other native wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip wheel \
    && pip wheel --no-deps --wheel-dir /wheels -r requirements.txt


# =========================
# Stage 2 — runtime image
# =========================
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

ARG APP_USER=appuser
ARG APP_HOME=/app
RUN useradd -m -d ${APP_HOME} -s /bin/bash ${APP_USER}

WORKDIR ${APP_HOME}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:_base.settings} \
    GUNICORN_WORKERS=3 \
    GUNICORN_BIND=0.0.0.0:8000 \
    GUNICORN_TIMEOUT=60 \
    GUNICORN_ACCESSLOG=- \
    GUNICORN_ERRORLOG=- \
    DJANGO_ENV=production

COPY --from=builder /wheels /wheels
RUN python -m pip install --upgrade pip \
    && pip install --no-index --find-links=/wheels /wheels/*

COPY . ${APP_HOME}

# Ensure media/static dirs exist (STATIC_ROOT should be set in settings)
RUN mkdir -p ${APP_HOME}/media ${APP_HOME}/staticfiles

# Make entrypoint executable
RUN chmod +x ${APP_HOME}/entrypoint.sh

# Switch to non-root
USER ${APP_USER}

EXPOSE 8000

ARG DJANGO_ENV=production
RUN if [ "$DJANGO_ENV" = "production" ]; then \
        echo "Collecting static assets..." && \
        python manage.py collectstatic --noinput || true ; \
    else \
        echo "Skipping collectstatic during build (DJANGO_ENV=$DJANGO_ENV)"; \
    fi

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -fsS http://127.0.0.1:8000/ || exit 1

ENV APP_MODULE=${APP_MODULE:-your_project.wsgi:application}

ENTRYPOINT ["./entrypoint.sh"]
CMD ["sh", "-c", "gunicorn ${APP_MODULE} --workers ${GUNICORN_WORKERS} --bind ${GUNICORN_BIND} --timeout ${GUNICORN_TIMEOUT} --access-logfile ${GUNICORN_ACCESSLOG} --error-logfile ${GUNICORN_ERRORLOG}"]
