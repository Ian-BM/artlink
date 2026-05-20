from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from artworks.models import Artwork, Certificate
from .models import Inquiry
from .forms import ArtworkForm, InquiryForm


def user_is_artist(user):
    """Return True only if the authenticated user has an artist profile."""
    return hasattr(user, 'profile') and user.profile.user_type == 'artist'


def user_is_buyer(user):
    """Return True only if the authenticated user has a buyer profile."""
    return hasattr(user, 'profile') and user.profile.user_type == 'buyer'

@login_required
def artist_dashboard(request):
    if not user_is_artist(request.user):
        messages.error(request, 'Access denied.')
        return redirect('home')
    artworks = Artwork.objects.filter(artist=request.user)
    total_uploaded = artworks.count()
    total_sold = artworks.filter(status='sold').count()
    active_listings = artworks.filter(status='available').count()
    inquiries = Inquiry.objects.filter(artwork__artist=request.user).order_by('-created_at')
    return render(request, 'dashboard/dashboard.html', {
        'total_uploaded': total_uploaded,
        'total_sold': total_sold,
        'active_listings': active_listings,
        'inquiries_count': inquiries.count(),
        'artworks': artworks,
        'inquiries': inquiries,
    })

@login_required
def upload_artwork(request):
    if not user_is_artist(request.user):
        messages.error(request, 'Access denied.')
        return redirect('home')
    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES)
        if form.is_valid():
            artwork = form.save(commit=False)
            artwork.artist = request.user
            artwork.save()
            
            # Create certificate with PDF if provided
            cert_pdf = request.FILES.get('certificate_pdf')
            Certificate.objects.create(
                artwork=artwork,
                certificate_pdf=cert_pdf if cert_pdf else None
            )
            messages.success(request, 'Artwork uploaded successfully!')
            return redirect('dashboard')
    else:
        form = ArtworkForm()
    return render(request, 'dashboard/upload.html', {'form': form})

@login_required
def inquiry_inbox(request):
    if not user_is_artist(request.user):
        messages.error(request, 'Access denied.')
        return redirect('home')
    inquiries = Inquiry.objects.filter(artwork__artist=request.user).order_by('-created_at')
    return render(request, 'dashboard/inquiries.html', {'inquiries': inquiries})

@login_required
def send_inquiry(request, artwork_id):
    artwork = get_object_or_404(Artwork, pk=artwork_id)
    if not user_is_buyer(request.user):
        messages.error(request, 'Only buyers can send inquiries.')
        return redirect('home')
    if artwork.artist == request.user:
        messages.error(request, 'You cannot inquire about your own artwork.')
        return redirect('dashboard')
    if artwork.status != 'available':
        messages.error(request, 'Only available artworks can receive inquiries.')
        return redirect('artwork_detail', pk=artwork_id)

    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.artwork = artwork
            inquiry.buyer = request.user
            inquiry.save()
            messages.success(request, 'Your message has been received. The artist will contact you via WhatsApp shortly.')
            return redirect('artwork_detail', pk=artwork_id)
    else:
        form = InquiryForm()
    return render(request, 'dashboard/inquiry_form.html', {'form': form, 'artwork': artwork})
