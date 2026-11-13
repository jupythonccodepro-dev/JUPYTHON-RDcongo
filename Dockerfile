FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN groupadd --system django \
    && useradd --system --gid django --home-dir /app django \
    && mkdir -p /app/media /app/staticfiles \
    && chown -R django:django /app/media /app/staticfiles
USER django
EXPOSE 8000
CMD ["gunicorn", "jupython.wsgi:application", "--bind=0.0.0.0:8000", "--workers=2", "--access-logfile=-", "--error-logfile=-", "--timeout=60"]
