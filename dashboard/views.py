from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from artworks.models import Artwork, Certificate, Exhibition
from accounts.models import Profile
from .models import Inquiry, CustomArtworkRequest
from .forms import ArtworkForm, InquiryForm, CustomArtworkRequestForm, CustomArtworkRequestStatusForm, ExhibitionForm


def user_is_artist(user):
    """Return True only if the authenticated user has an artist profile."""
    return hasattr(user, 'profile') and user.profile.user_type == 'artist'


def user_is_buyer(user):
    """Return True only if the authenticated user has a buyer profile."""
    return hasattr(user, 'profile') and user.profile.user_type == 'buyer'


def artist_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not user_is_artist(request.user):
            messages.error(request, 'Access denied.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def dashboard_metrics(user):
    artworks = Artwork.objects.filter(artist=user)
    inquiries = Inquiry.objects.filter(artwork__artist=user)
    custom_requests = CustomArtworkRequest.objects.filter(artist=user)
    exhibitions = Exhibition.objects.filter(artist=user)
    return {
        'total_uploaded': artworks.count(),
        'active_listings': artworks.filter(status='available').count(),
        'total_sold': artworks.filter(status='sold').count(),
        'inquiries_count': inquiries.count(),
        'custom_requests_count': custom_requests.count(),
        'exhibitions_count': exhibitions.count(),
        'published_exhibitions_count': exhibitions.filter(visibility='published').count(),
    }


def recent_activity(user, limit=8):
    activities = []
    for inquiry in Inquiry.objects.filter(artwork__artist=user).select_related('buyer', 'artwork')[:limit]:
        activities.append({
            'kind': 'Inquiry',
            'title': inquiry.artwork.title,
            'detail': f"{inquiry.buyer.get_full_name() or inquiry.buyer.username} sent a message",
            'timestamp': inquiry.created_at,
        })
    for custom_request in CustomArtworkRequest.objects.filter(artist=user)[:limit]:
        activities.append({
            'kind': 'Custom Request',
            'title': custom_request.get_artwork_type_display(),
            'detail': f"{custom_request.buyer_name} requested a commission",
            'timestamp': custom_request.created_at,
        })
    for exhibition in Exhibition.objects.filter(artist=user)[:limit]:
        activities.append({
            'kind': 'Exhibition',
            'title': exhibition.title,
            'detail': f"Exhibition marked {exhibition.get_visibility_display().lower()}",
            'timestamp': exhibition.updated_at,
        })
    activities.sort(key=lambda item: item['timestamp'], reverse=True)
    return activities[:limit]


@artist_required
def artist_dashboard(request):
    metrics = dashboard_metrics(request.user)
    return render(request, 'dashboard/overview.html', {
        'active_section': 'overview',
        'metrics': metrics,
        'recent_activity': recent_activity(request.user),
        'recent_inquiries': Inquiry.objects.filter(artwork__artist=request.user).select_related('buyer', 'artwork')[:4],
        'recent_custom_requests': CustomArtworkRequest.objects.filter(artist=request.user)[:4],
    })


@artist_required
def dashboard_artworks(request):
    artworks = Artwork.objects.filter(artist=request.user).order_by('-created_at')
    return render(request, 'dashboard/artworks.html', {
        'active_section': 'artworks',
        'metrics': dashboard_metrics(request.user),
        'artworks': artworks,
    })


@artist_required
def dashboard_sales(request):
    sold_artworks = Artwork.objects.filter(artist=request.user, status='sold').order_by('-updated_at')
    total_revenue = sum(artwork.price for artwork in sold_artworks)
    return render(request, 'dashboard/sales.html', {
        'active_section': 'sales',
        'metrics': dashboard_metrics(request.user),
        'sold_artworks': sold_artworks,
        'total_revenue': total_revenue,
    })


@artist_required
def upload_artwork(request):
    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES)
        if form.is_valid():
            artwork = form.save(commit=False)
            artwork.artist = request.user
            artwork.save()

            cert_pdf = request.FILES.get('certificate_pdf')
            Certificate.objects.create(
                artwork=artwork,
                certificate_pdf=cert_pdf if cert_pdf else None
            )
            messages.success(request, 'Artwork uploaded successfully!')
            return redirect('dashboard_artworks')
    else:
        form = ArtworkForm()
    return render(request, 'dashboard/upload.html', {
        'active_section': 'artworks',
        'form': form,
    })


@artist_required
def edit_artwork(request, artwork_id):
    artwork = get_object_or_404(Artwork, pk=artwork_id, artist=request.user)

    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES, instance=artwork)
        if form.is_valid():
            updated_artwork = form.save()
            cert_pdf = request.FILES.get('certificate_pdf')
            certificate, _ = Certificate.objects.get_or_create(artwork=updated_artwork)
            if cert_pdf:
                certificate.certificate_pdf = cert_pdf
                certificate.save()
            messages.success(request, 'Artwork updated successfully!')
            return redirect('dashboard_artworks')
    else:
        form = ArtworkForm(instance=artwork)

    certificate = getattr(artwork, 'certificate', None)
    return render(request, 'dashboard/edit_artwork.html', {
        'active_section': 'artworks',
        'form': form,
        'artwork': artwork,
        'certificate': certificate,
    })


@artist_required
@require_POST
def delete_artwork(request, artwork_id):
    artwork = get_object_or_404(Artwork, pk=artwork_id, artist=request.user)
    artwork.delete()
    messages.success(request, 'Artwork deleted successfully.')
    return redirect('dashboard_artworks')


@artist_required
@require_POST
def toggle_artwork_status(request, artwork_id):
    artwork = get_object_or_404(Artwork, pk=artwork_id, artist=request.user)
    next_status = request.POST.get('status')
    if next_status not in {'available', 'sold'}:
        messages.error(request, 'Invalid status update.')
        return redirect('dashboard_artworks')

    artwork.status = next_status
    artwork.save(update_fields=['status', 'updated_at'])

    sold_count = Artwork.objects.filter(artist=request.user, status='sold').count()
    profile = request.user.profile
    if profile.total_artworks_sold != sold_count:
        profile.total_artworks_sold = sold_count
        profile.save(update_fields=['total_artworks_sold'])

    messages.success(request, f'"{artwork.title}" is now marked as {artwork.get_status_display().lower()}.')
    return redirect('dashboard_artworks')


@artist_required
def inquiry_inbox(request):
    inquiries = Inquiry.objects.filter(artwork__artist=request.user).select_related('buyer', 'artwork').order_by('-created_at')
    return render(request, 'dashboard/inquiries.html', {
        'active_section': 'inquiries',
        'metrics': dashboard_metrics(request.user),
        'inquiries': inquiries,
    })


def request_custom_artwork(request, artist_id):
    artist = get_object_or_404(User, pk=artist_id, profile__user_type='artist')
    profile = get_object_or_404(Profile, user=artist)

    initial = {}
    if request.user.is_authenticated:
        initial = {
            'buyer_name': request.user.get_full_name() or request.user.username,
            'buyer_email': request.user.email,
            'buyer_whatsapp': getattr(request.user.profile, 'phone_number', '') if hasattr(request.user, 'profile') else '',
        }

    if request.method == 'POST':
        form = CustomArtworkRequestForm(request.POST, request.FILES)
        if form.is_valid():
            custom_request = form.save(commit=False)
            custom_request.artist = artist
            custom_request.save()
            messages.success(request, 'Your custom artwork request has been sent. The artist will contact you directly.')
            return redirect('artist_profile', pk=artist.pk)
    else:
        form = CustomArtworkRequestForm(initial=initial)

    return render(request, 'dashboard/custom_request_form.html', {
        'form': form,
        'artist': artist,
        'profile': profile,
    })


@artist_required
def custom_request_inbox(request):
    custom_requests = CustomArtworkRequest.objects.filter(artist=request.user).order_by('-created_at')
    return render(request, 'dashboard/custom_requests.html', {
        'active_section': 'custom_requests',
        'metrics': dashboard_metrics(request.user),
        'custom_requests': custom_requests,
    })


@artist_required
@require_POST
def update_custom_request_status(request, request_id):
    custom_request = get_object_or_404(CustomArtworkRequest, pk=request_id, artist=request.user)
    form = CustomArtworkRequestStatusForm(request.POST, instance=custom_request)
    if form.is_valid():
        form.save()
        messages.success(request, 'Custom request status updated.')
    else:
        messages.error(request, 'Invalid custom request status.')
    return redirect('custom_request_inbox')


@artist_required
def dashboard_exhibitions(request):
    exhibitions = Exhibition.objects.filter(artist=request.user).prefetch_related('artworks').order_by('-updated_at')
    return render(request, 'dashboard/exhibitions.html', {
        'active_section': 'exhibitions',
        'metrics': dashboard_metrics(request.user),
        'exhibitions': exhibitions,
    })


@artist_required
def create_exhibition(request):
    if request.method == 'POST':
        form = ExhibitionForm(request.POST, request.FILES, artist=request.user)
        if form.is_valid():
            exhibition = form.save(commit=False)
            exhibition.artist = request.user
            exhibition.save()
            form.save_m2m()
            messages.success(request, 'Exhibition created successfully.')
            return redirect('dashboard_exhibitions')
    else:
        form = ExhibitionForm(artist=request.user)
    return render(request, 'dashboard/exhibition_form.html', {
        'active_section': 'exhibitions',
        'form': form,
        'form_mode': 'create',
    })


@artist_required
def edit_exhibition(request, exhibition_id):
    exhibition = get_object_or_404(Exhibition, pk=exhibition_id, artist=request.user)
    if request.method == 'POST':
        form = ExhibitionForm(request.POST, request.FILES, instance=exhibition, artist=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exhibition updated successfully.')
            return redirect('dashboard_exhibitions')
    else:
        form = ExhibitionForm(instance=exhibition, artist=request.user)
    return render(request, 'dashboard/exhibition_form.html', {
        'active_section': 'exhibitions',
        'form': form,
        'exhibition': exhibition,
        'form_mode': 'edit',
    })


@artist_required
@require_POST
def delete_exhibition(request, exhibition_id):
    exhibition = get_object_or_404(Exhibition, pk=exhibition_id, artist=request.user)
    exhibition.delete()
    messages.success(request, 'Exhibition deleted successfully.')
    return redirect('dashboard_exhibitions')


@artist_required
@require_POST
def toggle_exhibition_visibility(request, exhibition_id):
    exhibition = get_object_or_404(Exhibition, pk=exhibition_id, artist=request.user)
    next_visibility = request.POST.get('visibility')
    if next_visibility not in {'draft', 'published'}:
        messages.error(request, 'Invalid exhibition visibility.')
        return redirect('dashboard_exhibitions')
    exhibition.visibility = next_visibility
    exhibition.save(update_fields=['visibility', 'updated_at'])
    messages.success(request, f'"{exhibition.title}" is now {exhibition.get_visibility_display().lower()}.')
    return redirect('dashboard_exhibitions')


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
