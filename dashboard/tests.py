from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile
from artworks.models import Artwork
from .models import Inquiry


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
