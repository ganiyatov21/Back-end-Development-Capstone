# Back-end-Development-Capstone

Django band website integrating the Pictures and Songs Flask microservices.
Includes signup, login/logout, concerts and attendance, song lyric modals,
photo gallery, and Django admin.

## Setup
Use Python 3.9+ and install `requirements.txt` into a virtual environment.
Run `python manage.py makemigrations`, `python manage.py migrate`,
`python manage.py collectstatic --noinput`, and `python manage.py test concert`.
Run `python manage.py runserver 0.0.0.0:8000` for local development.

Set PICTURES_SERVICE_URL and SONGS_SERVICE_URL to the running microservice URLs.
For deployment provide DJANGO_SECRET_KEY and optionally DJANGO_ALLOWED_HOSTS.
DJANGO_DEBUG=1 enables development diagnostics; debug is off by default.
Photos and Songs are unmanaged models representing external resources.
Seven Django tests cover authentication, attendance and service integration.

The Dockerfile serves static assets with WhiteNoise and applies migrations.
Optional initial admin creation requires DJANGO_SUPERUSER_USERNAME,
DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD; credentials are not committed.
SQLite data is ephemeral in the course Kubernetes pod. Keep one replica;
use a persistent database before using this project outside the temporary lab.

## Kubernetes lab deployment

Build and push `us.icr.io/sn-labs-u46lawgunnel/djangoserver:1`, then create the
`django-config` secret with a freshly generated `secret-key` value. Apply
`kubectl apply -f deployment.yml` and forward port 8000 from the running pod.
The manifest contains the service URLs verified in the lab on 2026-10-29.
SN Labs resources and proxy addresses expire when the lab is reset or idle.
Update both service URLs and the registry namespace for another lab account.

The legacy public OpenShift route was unreachable from this lab. The Songs
service still runs on OpenShift with a real MongoDB 7.0 instance; access uses
`oc port-forward service/songs 5000:8080` and the SN Labs HTTPS port proxy.
