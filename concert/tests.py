from unittest.mock import patch
from datetime import date
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Concert, ConcertAttending

class BandWebsiteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("listener", password="Test-only-pass-123")
        self.concert = Concert.objects.create(concert_name="Capstone Live", duration=2, city="Almaty", date=date(2030, 11, 2))
    def test_home(self):
        self.assertEqual(self.client.get(reverse("index")).status_code, 200)
    def test_signup_and_login(self):
        response = self.client.post(reverse("signup"), {"username": "newlistener", "password": "Test-only-pass-123"})
        self.assertRedirects(response, reverse("index"))
        self.assertTrue(User.objects.get(username="newlistener").check_password("Test-only-pass-123"))
        self.client.logout()
        self.assertRedirects(self.client.post(reverse("login"), {"username": "newlistener", "password": "Test-only-pass-123"}), reverse("index"))
    def test_duplicate_signup(self):
        response = self.client.post(reverse("signup"), {"username": "listener", "password": "Test-only-pass-123"})
        self.assertContains(response, "already taken")
    def test_authentication_required_for_concerts(self):
        self.assertEqual(self.client.get(reverse("concerts")).status_code, 302)
    def test_attendance(self):
        self.client.force_login(self.user)
        self.assertContains(self.client.get(reverse("concerts")), "Capstone Live")
        self.client.post(reverse("concert_attendee"), {"concert_id": self.concert.id, "attendee_choice": "Attending"})
        self.assertEqual(ConcertAttending.objects.get(user=self.user).attending, "Attending")
        self.assertEqual(self.client.post(reverse("concert_attendee"), {"concert_id": self.concert.id, "attendee_choice": "invalid"}).status_code, 400)
    @patch("concert.views.requests.get")
    def test_song_service_and_modal(self, get):
        get.return_value.json.return_value = {"songs": [{"id": 1, "title": "Test Song", "lyrics": "Test lyrics"}]}
        response = self.client.get(reverse("songs"))
        self.assertContains(response, "Test Song")
        self.assertContains(response, "Test lyrics")
    @patch("concert.views.requests.get")
    def test_photo_service(self, get):
        get.return_value.json.return_value = [{"id": 1, "pic_url": "https://example.com/photo.jpg", "event_city": "Almaty", "event_state": "Almaty", "event_date": "2030-11-02"}]
        self.assertContains(self.client.get(reverse("photos")), "Almaty")
