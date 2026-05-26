from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import ArtistProfileForm
from .models import Profile


class ArtistProfileEditTests(TestCase):
    def setUp(self):
        self.artist = User.objects.create_user(
            username='oldname',
            email='old@example.com',
            password='strong-pass-123',
        )
        self.artist_profile = Profile.objects.create(
            user=self.artist,
            user_type='artist',
            bio='Old bio',
        )

        self.buyer = User.objects.create_user(
            username='buyer@example.com',
            email='buyer@example.com',
            password='strong-pass-123',
        )
        Profile.objects.create(user=self.buyer, user_type='buyer')

    def test_artist_can_update_user_and_profile_fields(self):
        self.client.login(username='oldname', password='strong-pass-123')

        response = self.client.post(reverse('edit_artist_profile'), {
            'username': 'newname',
            'first_name': 'Ada',
            'last_name': 'Painter',
            'email': 'new@example.com',
            'bio': 'New bio',
            'location': 'Nairobi',
            'phone_number': '+254 700000000',
            'certifications': 'Gallery resident',
        })

        self.assertRedirects(response, reverse('artist_profile', kwargs={'pk': self.artist.pk}))
        self.artist.refresh_from_db()
        self.artist_profile.refresh_from_db()
        self.assertEqual(self.artist.username, 'newname')
        self.assertEqual(self.artist.email, 'new@example.com')
        self.assertEqual(self.artist.first_name, 'Ada')
        self.assertEqual(self.artist_profile.bio, 'New bio')
        self.assertEqual(self.artist_profile.location, 'Nairobi')
        self.assertEqual(self.artist_profile.certifications, 'Gallery resident')

    def test_buyer_cannot_edit_artist_profile(self):
        self.client.login(username='buyer@example.com', password='strong-pass-123')

        response = self.client.get(reverse('edit_artist_profile'))

        self.assertRedirects(response, reverse('home'))

    def test_artist_profile_form_rejects_duplicate_username_and_email(self):
        User.objects.create_user(
            username='taken',
            email='taken@example.com',
            password='strong-pass-123',
        )

        form = ArtistProfileForm(
            data={
                'username': 'taken',
                'first_name': '',
                'last_name': '',
                'email': 'taken@example.com',
                'bio': '',
                'location': '',
                'phone_number': '',
                'certifications': '',
            },
            instance=self.artist_profile,
            user=self.artist,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)


class RoleBasedAuthRedirectTests(TestCase):
    def setUp(self):
        self.artist = User.objects.create_user(
            username='artist',
            email='artist@example.com',
            password='Strongpass123!',
        )
        Profile.objects.create(user=self.artist, user_type='artist')

        self.buyer = User.objects.create_user(
            username='buyer@example.com',
            email='buyer@example.com',
            password='Strongpass123!',
        )
        Profile.objects.create(user=self.buyer, user_type='buyer')

    def test_artist_login_redirects_to_dashboard(self):
        response = self.client.post(reverse('login'), {
            'username': 'artist',
            'password': 'Strongpass123!',
        })

        self.assertRedirects(response, reverse('dashboard'), fetch_redirect_response=False)

    def test_buyer_login_redirects_to_homepage(self):
        response = self.client.post(reverse('login'), {
            'username': 'buyer@example.com',
            'password': 'Strongpass123!',
        })

        self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)

    def test_artist_signup_logs_in_and_redirects_to_dashboard(self):
        response = self.client.post(reverse('register_artist'), {
            'username': 'newartist',
            'email': 'newartist@example.com',
            'password': 'Strongpass123!',
            'password_confirm': 'Strongpass123!',
        })

        self.assertRedirects(response, reverse('dashboard'), fetch_redirect_response=False)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.profile.user_type, 'artist')

    def test_buyer_signup_logs_in_and_redirects_to_homepage(self):
        response = self.client.post(reverse('register_buyer'), {
            'first_name': 'New',
            'last_name': 'Buyer',
            'email': 'newbuyer@example.com',
            'country_code': '+254',
            'phone_number': '700000000',
            'password': 'Strongpass123!',
            'password_confirm': 'Strongpass123!',
        })

        self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.profile.user_type, 'buyer')
