FROM python:3.9-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput && chmod +x entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
CMD ["gunicorn", "django_concert.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "1"]
