from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile
from .forms import BuyerRegistrationForm, ArtistRegistrationForm

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
            messages.success(request, 'Buyer account created successfully! You can now login.')
            return redirect('login')
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
            messages.success(request, 'Artist account created successfully! You can now login.')
            return redirect('login')
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


from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('home')
