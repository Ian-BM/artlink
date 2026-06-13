import re
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from .models import Artwork, Certificate, Exhibition
from accounts.models import Profile
from django.contrib.auth.models import User

def published_exhibitions():
    return Exhibition.objects.filter(visibility='published')


def home(request):
    featured_artworks = Artwork.objects.select_related('artist').order_by('-created_at')[:6]
    featured_artists = Profile.objects.filter(user_type='artist')[:4]
    featured_exhibition = published_exhibitions().filter(featured=True).first()
    return render(request, 'artworks/home.html', {
        'featured_artworks': featured_artworks,
        'featured_artists': featured_artists,
        'featured_exhibition': featured_exhibition,
    })

def marketplace(request):
    artworks = Artwork.objects.select_related('artist').order_by('-created_at')
    # Add filtering logic here if needed
    return render(request, 'artworks/marketplace.html', {'artworks': artworks})

def artwork_detail(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)
    certificate = Certificate.objects.filter(artwork=artwork).first()
    return render(request, 'artworks/artwork_detail.html', {
        'artwork': artwork,
        'certificate': certificate,
    })

def artist_profile(request, pk):
    artist = get_object_or_404(User, pk=pk)
    profile = get_object_or_404(Profile, user=artist)
    artworks = Artwork.objects.filter(artist=artist).order_by('-created_at')
    return render(request, 'artworks/artist_profile.html', {
        'artist': artist,
        'profile': profile,
        'artworks': artworks,
    })

def artists_list(request):
    artists = Profile.objects.filter(user_type='artist')
    return render(request, 'artworks/artists.html', {'artists': artists})

def verify_certificate(request):
    certificate = None
    certificate_status = None
    if request.method == 'POST':
        cert_id = request.POST.get('certificate_id', '') or ''
        cert_id = cert_id.strip().strip('“”"\'')
        match = re.search(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', cert_id)
        if match:
            clean_id = match.group(0)
            certificate = Certificate.objects.filter(certificate_id=clean_id).first()
            if certificate:
                certificate_status = 'verified' if certificate.certificate_pdf else 'not_verified'
            else:
                certificate_status = 'not_found'
        else:
            certificate_status = 'invalid'
    return render(request, 'artworks/verify.html', {
        'certificate': certificate,
        'certificate_status': certificate_status,
    })


def exhibitions_home(request):
    today = timezone.localdate()
    exhibitions = published_exhibitions().select_related('artist', 'artist__profile').prefetch_related('artworks')
    featured_exhibition = exhibitions.filter(featured=True).first()
    current_exhibitions = exhibitions.filter(start_date__lte=today, end_date__gte=today)
    past_exhibitions = exhibitions.filter(end_date__lt=today)
    return render(request, 'artworks/exhibitions.html', {
        'featured_exhibition': featured_exhibition,
        'current_exhibitions': current_exhibitions,
        'past_exhibitions': past_exhibitions,
    })


def exhibition_detail(request, slug):
    exhibition = get_object_or_404(
        published_exhibitions().select_related('artist', 'artist__profile').prefetch_related('artworks__artist__profile'),
        slug=slug,
    )
    artworks = exhibition.artworks.select_related('artist', 'artist__profile').all()
    return render(request, 'artworks/exhibition_detail.html', {
        'exhibition': exhibition,
        'artworks': artworks,
        'artist_profile': exhibition.artist.profile,
    })


def exhibition_gallery(request, slug):
    exhibition = get_object_or_404(
        published_exhibitions().prefetch_related('artworks__artist__profile'),
        slug=slug,
    )
    artworks = exhibition.artworks.select_related('artist', 'artist__profile').all()
    artwork_data = []
    for artwork in artworks:
        image_url = ''
        if artwork.images:
            image_url = request.build_absolute_uri(artwork.images.url)
        profile = getattr(artwork.artist, 'profile', None)
        artwork_data.append({
            'id': artwork.pk,
            'title': artwork.title,
            'artist': artwork.artist.username,
            'artistProfileUrl': reverse('artist_profile', kwargs={'pk': artwork.artist.pk}),
            'price': str(artwork.price),
            'description': artwork.description,
            'artistStatement': profile.artist_statement if profile else '',
            'medium': artwork.get_medium_display(),
            'dimensions': artwork.size,
            'availability': artwork.get_status_display(),
            'imageUrl': image_url,
            'detailUrl': reverse('artwork_detail', kwargs={'pk': artwork.pk}),
        })
    return render(request, 'artworks/exhibition_gallery.html', {
        'exhibition': exhibition,
        'artworks': artworks,
        'artwork_data': artwork_data,
    })
