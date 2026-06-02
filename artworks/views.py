import re
from django.shortcuts import render, get_object_or_404
from .models import Artwork, Certificate
from accounts.models import Profile
from django.contrib.auth.models import User

def home(request):
    featured_artworks = Artwork.objects.select_related('artist').order_by('-created_at')[:6]
    featured_artists = Profile.objects.filter(user_type='artist')[:4]
    return render(request, 'artworks/home.html', {
        'featured_artworks': featured_artworks,
        'featured_artists': featured_artists,
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
