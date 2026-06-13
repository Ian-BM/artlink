from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile
from artworks.models import Artwork
from .models import Inquiry, CustomArtworkRequest


class ArtistInquiryInboxTests(TestCase):
    def setUp(self):
        self.artist = User.objects.create_user(
            username='artist',
            email='artist@example.com',
            password='Strongpass123!',
        )
        Profile.objects.create(user=self.artist, user_type='artist')

        self.other_artist = User.objects.create_user(
            username='otherartist',
            email='otherartist@example.com',
            password='Strongpass123!',
        )
        Profile.objects.create(user=self.other_artist, user_type='artist')

        self.buyer = User.objects.create_user(
            username='buyer@example.com',
            email='buyer@example.com',
            password='Strongpass123!',
            first_name='Buyer',
            last_name='One',
        )
        Profile.objects.create(user=self.buyer, user_type='buyer')

        self.artist_artwork = Artwork.objects.create(
            artist=self.artist,
            title='Visible Artwork',
            description='Visible description',
            price='100.00',
            medium='oil',
            size='20x20',
            year_created=2025,
        )
        self.other_artwork = Artwork.objects.create(
            artist=self.other_artist,
            title='Hidden Artwork',
            description='Hidden description',
            price='200.00',
            medium='acrylic',
            size='30x30',
            year_created=2025,
        )

        Inquiry.objects.create(
            buyer=self.buyer,
            artwork=self.artist_artwork,
            message='Visible inquiry message',
        )
        Inquiry.objects.create(
            buyer=self.buyer,
            artwork=self.other_artwork,
            message='Hidden inquiry message',
        )

    def test_artist_inquiries_route_filters_to_current_artist_artworks(self):
        self.client.login(username='artist', password='Strongpass123!')

        response = self.client.get(reverse('artist_inquiries'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Visible Artwork')
        self.assertContains(response, 'Visible inquiry message')
        self.assertNotContains(response, 'Hidden Artwork')
        self.assertNotContains(response, 'Hidden inquiry message')
        self.assertContains(response, 'Reply via Email')

    def test_buyer_cannot_access_artist_inquiries(self):
        self.client.login(username='buyer@example.com', password='Strongpass123!')

        response = self.client.get(reverse('artist_inquiries'))

        self.assertRedirects(response, reverse('home'))


class CustomArtworkRequestTests(TestCase):
    def setUp(self):
        self.artist = User.objects.create_user(
            username='commissionartist',
            email='commissionartist@example.com',
            password='Strongpass123!',
        )
        Profile.objects.create(user=self.artist, user_type='artist')

        self.other_artist = User.objects.create_user(
            username='othercommissionartist',
            email='othercommissionartist@example.com',
            password='Strongpass123!',
        )
        Profile.objects.create(user=self.other_artist, user_type='artist')

        self.buyer = User.objects.create_user(
            username='collector@example.com',
            email='collector@example.com',
            password='Strongpass123!',
            first_name='Collector',
            last_name='One',
        )
        Profile.objects.create(user=self.buyer, user_type='buyer', phone_number='+254 700000000')

    def test_buyer_can_submit_custom_request_to_artist(self):
        self.client.login(username='collector@example.com', password='Strongpass123!')

        response = self.client.post(reverse('request_custom_artwork', kwargs={'artist_id': self.artist.pk}), {
            'buyer_name': 'Collector One',
            'buyer_email': 'collector@example.com',
            'buyer_whatsapp': '+254 700000000',
            'artwork_type': 'portrait',
            'budget': '750.00',
            'deadline': '2026-08-01',
            'description': 'A museum-style portrait commission.',
        })

        self.assertRedirects(response, reverse('artist_profile', kwargs={'pk': self.artist.pk}))
        custom_request = CustomArtworkRequest.objects.get(artist=self.artist)
        self.assertEqual(custom_request.buyer_name, 'Collector One')
        self.assertEqual(custom_request.status, 'new')

    def test_artist_custom_request_inbox_is_scoped_to_artist(self):
        CustomArtworkRequest.objects.create(
            artist=self.artist,
            buyer_name='Visible Buyer',
            buyer_email='visible@example.com',
            buyer_whatsapp='+254 711111111',
            artwork_type='abstract',
            budget='500.00',
            description='Visible request',
        )
        CustomArtworkRequest.objects.create(
            artist=self.other_artist,
            buyer_name='Hidden Buyer',
            buyer_email='hidden@example.com',
            artwork_type='landscape',
            budget='900.00',
            description='Hidden request',
        )
        self.client.login(username='commissionartist', password='Strongpass123!')

        response = self.client.get(reverse('custom_request_inbox'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Visible Buyer')
        self.assertNotContains(response, 'Hidden Buyer')

    def test_artist_can_update_custom_request_status(self):
        custom_request = CustomArtworkRequest.objects.create(
            artist=self.artist,
            buyer_name='Status Buyer',
            buyer_email='status@example.com',
            artwork_type='pet_portrait',
            budget='300.00',
            description='Status request',
        )
        self.client.login(username='commissionartist', password='Strongpass123!')

        response = self.client.post(reverse('update_custom_request_status', kwargs={'request_id': custom_request.pk}), {
            'status': 'contacted',
        })

        self.assertRedirects(response, reverse('custom_request_inbox'))
        custom_request.refresh_from_db()
        self.assertEqual(custom_request.status, 'contacted')
