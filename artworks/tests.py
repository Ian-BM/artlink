from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Profile
from .models import Artwork, Exhibition


class ExhibitionViewsTests(TestCase):
    def setUp(self):
        self.artist = User.objects.create_user(
            username='exhibitionartist',
            email='exhibitionartist@example.com',
            password='Strongpass123!',
        )
        Profile.objects.create(
            user=self.artist,
            user_type='artist',
            artist_statement='I work with light, memory, and material presence.',
        )
        self.artwork = Artwork.objects.create(
            artist=self.artist,
            title='Gallery Work',
            description='A work for an online exhibition.',
            price='1200.00',
            medium='mixed',
            size='40x50',
            year_created=2026,
        )
        today = timezone.localdate()
        self.exhibition = Exhibition.objects.create(
            title='Digital Salon',
            description='A curated exhibition statement.',
            curator_name='ArtLink Curator',
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=10),
            featured=True,
        )
        self.exhibition.artworks.add(self.artwork)

    def test_exhibitions_home_lists_current_exhibition(self):
        response = self.client.get(reverse('exhibitions'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Digital Salon')
        self.assertContains(response, 'Current Exhibitions')

    def test_exhibition_detail_shows_artworks_and_virtual_gallery_link(self):
        response = self.client.get(reverse('exhibition_detail', kwargs={'slug': self.exhibition.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gallery Work')
        self.assertContains(response, 'Enter Virtual Gallery')
        self.assertContains(response, 'I work with light')

    def test_exhibition_gallery_serializes_artwork_data(self):
        response = self.client.get(reverse('exhibition_gallery', kwargs={'slug': self.exhibition.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'gallery-artworks')
        self.assertContains(response, 'Gallery Work')
