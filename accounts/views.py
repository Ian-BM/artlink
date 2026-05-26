from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.views.decorators.http import require_POST
from .models import Profile
from .forms import BuyerRegistrationForm, ArtistRegistrationForm, ArtistProfileForm


def role_based_redirect_url(user):
    if hasattr(user, 'profile') and user.profile.user_type == 'artist':
        return reverse('dashboard')
    return reverse('home')


class RoleBasedLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_default_redirect_url(self):
        return role_based_redirect_url(self.request.user)

def register_choice(request):
    return render(request, 'accounts/register_choice.html')

def register_buyer(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = BuyerRegistrationForm(request.POST)
        if form.is_valid():
            # Create user
            user = User.objects.create_user(
                username=form.cleaned_data['email'],  # Use email as username for buyers
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            
            # Create buyer profile
            country_code = form.cleaned_data['country_code']
            phone_number = form.cleaned_data['phone_number']
            Profile.objects.create(
                user=user,
                user_type='buyer',
                phone_number=f"{country_code} {phone_number}"
            )
            login(request, user)
            messages.success(request, 'Buyer account created successfully!')
            return redirect(role_based_redirect_url(user))
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = BuyerRegistrationForm()
    
    return render(request, 'accounts/register_buyer.html', {'form': form})

def register_artist(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = ArtistRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Create user
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            
            # Create artist profile with profile picture
            profile_picture = request.FILES.get('profile_picture')
            Profile.objects.create(
                user=user,
                user_type='artist',
                profile_image=profile_picture if profile_picture else None
            )
            login(request, user)
            messages.success(request, 'Artist account created successfully!')
            return redirect(role_based_redirect_url(user))
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ArtistRegistrationForm()
    
    return render(request, 'accounts/register_artist.html', {'form': form})

def register(request):
    return redirect('register_choice')


@login_required
def edit_artist_profile(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'artist':
        messages.error(request, 'Only artist accounts can edit an artist profile.')
        return redirect('home')

    if request.method == 'POST':
        form = ArtistProfileForm(
            request.POST,
            request.FILES,
            instance=request.user.profile,
            user=request.user,
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Your artist profile has been updated.')
            return redirect('artist_profile', pk=request.user.pk)
    else:
        form = ArtistProfileForm(instance=request.user.profile, user=request.user)

    return render(request, 'accounts/edit_artist_profile.html', {'form': form})


@require_POST
def logout_view(request):
    """Log out the authenticated user using POST only.

    Using POST for logout prevents CSRF attacks via a GET request.
    """
    logout(request)
    return redirect('home')
