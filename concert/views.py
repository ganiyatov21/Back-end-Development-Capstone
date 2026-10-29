from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_POST
from concert.forms import LoginForm, SignUpForm
from concert.models import Concert, ConcertAttending
import requests


def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            form.add_error("username", "This username is already taken.")
        else:
            user = User.objects.create_user(username=username, password=form.cleaned_data["password"])
            login(request, user)
            return redirect("index")
    return render(request, "signup.html", {"form": form})


def index(request):
    return render(request, "index.html")


def fetch_service(base, path, key):
    try:
        response = requests.get(base.rstrip("/") + path, timeout=8)
        response.raise_for_status()
        payload = response.json()
        items = payload.get(key, []) if isinstance(payload, dict) else payload
        if not isinstance(items, list):
            raise ValueError("Invalid service response")
        return items, None
    except (requests.RequestException, ValueError):
        return [], "The service is temporarily unavailable. Please try again later."


def songs(request):
    items, error = fetch_service(settings.SONGS_SERVICE_URL, "/song", "songs")
    return render(request, "songs.html", {"songs": items, "service_error": error})


def photos(request):
    items, error = fetch_service(settings.PICTURES_SERVICE_URL, "/picture", "pictures")
    return render(request, "photos.html", {"photos": items, "service_error": error})


def login_view(request):
    form = LoginForm(request=request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("index")
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("index")


@login_required(login_url="login")
def concerts(request):
    statuses = dict(ConcertAttending.objects.filter(user=request.user).values_list("concert_id", "attending"))
    rows = [{"concert": concert, "status": statuses.get(concert.id, "-")} for concert in Concert.objects.order_by("date", "id")]
    return render(request, "concerts.html", {"concerts": rows})


@login_required(login_url="login")
def concert_detail(request, id):
    concert = get_object_or_404(Concert, pk=id)
    attendance = concert.attendee.filter(user=request.user).first()
    return render(request, "concert_detail.html", {"concert_details": concert, "status": attendance.attending if attendance else "-", "attending_choices": ConcertAttending.AttendingChoices.choices})


@login_required(login_url="login")
@require_POST
def concert_attendee(request):
    status = request.POST.get("attendee_choice")
    if status not in ConcertAttending.AttendingChoices.values:
        return HttpResponseBadRequest("Invalid attendance choice")
    concert = get_object_or_404(Concert, pk=request.POST.get("concert_id"))
    ConcertAttending.objects.update_or_create(concert=concert, user=request.user, defaults={"attending": status})
    return redirect("concerts")
