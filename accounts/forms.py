from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from .models import Profile

COUNTRY_CODES = [
    ('+1', '🇺🇸 United States - +1'),
    ('+44', '🇬🇧 United Kingdom - +44'),
    ('+91', '🇮🇳 India - +91'),
    ('+86', '🇨🇳 China - +86'),
    ('+81', '🇯🇵 Japan - +81'),
    ('+33', '🇫🇷 France - +33'),
    ('+49', '🇩🇪 Germany - +49'),
    ('+39', '🇮🇹 Italy - +39'),
    ('+34', '🇪🇸 Spain - +34'),
    ('+55', '🇧🇷 Brazil - +55'),
    ('+61', '🇦🇺 Australia - +61'),
    ('+64', '🇳🇿 New Zealand - +64'),
    ('+1', '🇨🇦 Canada - +1'),
    ('+52', '🇲🇽 Mexico - +52'),
    ('+56', '🇨🇱 Chile - +56'),
    ('+57', '🇨🇴 Colombia - +57'),
    ('+54', '🇦🇷 Argentina - +54'),
    ('+971', '🇦🇪 UAE - +971'),
    ('+966', '🇸🇦 Saudi Arabia - +966'),
    ('+47', '🇳🇴 Norway - +47'),
    ('+46', '🇸🇪 Sweden - +46'),
    ('+31', '🇳🇱 Netherlands - +31'),
    ('+32', '🇧🇪 Belgium - +32'),
    ('+41', '🇨🇭 Switzerland - +41'),
    ('+43', '🇦🇹 Austria - +43'),
    ('+48', '🇵🇱 Poland - +48'),
    ('+30', '🇬🇷 Greece - +30'),
    ('+351', '🇵🇹 Portugal - +351'),
    ('+45', '🇩🇰 Denmark - +45'),
    ('+358', '🇫🇮 Finland - +358'),
    ('+60', '🇲🇾 Malaysia - +60'),
    ('+65', '🇸🇬 Singapore - +65'),
    ('+66', '🇹🇭 Thailand - +66'),
    ('+62', '🇮🇩 Indonesia - +62'),
    ('+63', '🇵🇭 Philippines - +63'),
    # African Countries
    ('+213', '🇩🇿 Algeria - +213'),
    ('+244', '🇦🇴 Angola - +244'),
    ('+267', '🇧🇼 Botswana - +267'),
    ('+257', '🇧🇮 Burundi - +257'),
    ('+237', '🇨🇲 Cameroon - +237'),
    ('+225', '🇨🇮 Côte d\'Ivoire - +225'),
    ('+20', '🇪🇬 Egypt - +20'),
    ('+251', '🇪🇹 Ethiopia - +251'),
    ('+233', '🇬🇭 Ghana - +233'),
    ('+224', '🇬🇳 Guinea - +224'),
    ('+254', '🇰🇪 Kenya - +254'),
    ('+218', '🇱🇾 Libya - +218'),
    ('+265', '🇲🇼 Malawi - +265'),
    ('+223', '🇲🇱 Mali - +223'),
    ('+212', '🇲🇦 Morocco - +212'),
    ('+258', '🇲🇿 Mozambique - +258'),
    ('+264', '🇳🇦 Namibia - +264'),
    ('+234', '🇳🇬 Nigeria - +234'),
    ('+250', '🇷🇼 Rwanda - +250'),
    ('+221', '🇸🇳 Senegal - +221'),
    ('+27', '🇿🇦 South Africa - +27'),
    ('+249', '🇸🇩 Sudan - +249'),
    ('+255', '🇹🇿 Tanzania - +255'),
    ('+216', '🇹🇳 Tunisia - +216'),
    ('+256', '🇺🇬 Uganda - +256'),
    ('+260', '🇿🇲 Zambia - +260'),
    ('+263', '🇿🇼 Zimbabwe - +263'),
    ('+229', '🇧🇯 Benin - +229'),
]

class BuyerRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=150, required=True, label="Last Name")
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Password")
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True, label="Confirm Password")
    country_code = forms.ChoiceField(choices=COUNTRY_CODES, required=True, label="Country Code")
    phone_number = forms.CharField(max_length=20, required=True, label="Phone Number")

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean(self):
        # Normalize and validate all buyer registration fields.
        # This ensures email collisions cannot be used to create duplicate buyer accounts.
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        country_code = cleaned_data.get('country_code')
        phone_number = cleaned_data.get('phone_number')
        email = cleaned_data.get('email')

        if email:
            email = email.strip().lower()
            cleaned_data['email'] = email

        if not first_name:
            raise forms.ValidationError("First name is required.")
        if not last_name:
            raise forms.ValidationError("Last name is required.")
        if not country_code:
            raise forms.ValidationError("Country code is required.")
        if not phone_number:
            raise forms.ValidationError("Phone number is required.")
        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        if password:
            try:
                validate_password(password)
            except ValidationError as exc:
                raise forms.ValidationError(exc.messages)
        if email and (User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists()):
            raise forms.ValidationError("A user with this email address already exists.")
        
        return cleaned_data

class ArtistRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Password")
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True, label="Confirm Password")
    email = forms.EmailField(required=True)
    profile_picture = forms.ImageField(
        required=False,
        label="Profile Picture",
        help_text="Upload a valid image file.",
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])],
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Share who you are as an artist...'}),
    )
    artist_statement = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your artistic vision, inspiration, and creative process...'}),
    )
    location = forms.CharField(max_length=100, required=False)
    instagram_url = forms.URLField(required=False, label="Instagram URL")
    tiktok_url = forms.URLField(required=False, label="TikTok URL")
    facebook_url = forms.URLField(required=False, label="Facebook URL")
    website_url = forms.URLField(required=False, label="Website URL")

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean(self):
        # Enforce strong password rules and unique username/email for artists.
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        username = cleaned_data.get('username')

        if not username:
            raise forms.ValidationError("Username is required.")
        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        if password:
            try:
                validate_password(password)
            except ValidationError as exc:
                raise forms.ValidationError(exc.messages)
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")

        email = cleaned_data.get('email')
        if email:
            email = email.strip().lower()
            cleaned_data['email'] = email
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("A user with this email address already exists.")
        
        return cleaned_data


class ArtistProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, label="Artist Name")
    first_name = forms.CharField(max_length=30, required=False, label="First Name")
    last_name = forms.CharField(max_length=150, required=False, label="Last Name")
    email = forms.EmailField(required=True)
    profile_image = forms.ImageField(
        required=False,
        label="Profile Picture",
        help_text="Upload a valid image file.",
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])],
    )

    class Meta:
        model = Profile
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'bio',
            'artist_statement',
            'location',
            'phone_number',
            'instagram_url',
            'tiktok_url',
            'facebook_url',
            'website_url',
            'profile_image',
            'certifications',
        )
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Tell collectors about your work, process, and story...'}),
            'artist_statement': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Describe your artistic vision, themes, and inspiration...'}),
            'certifications': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Awards, exhibitions, training, or certifications...'}),
            'instagram_url': forms.URLInput(attrs={'placeholder': 'https://instagram.com/your-handle'}),
            'tiktok_url': forms.URLInput(attrs={'placeholder': 'https://tiktok.com/@your-handle'}),
            'facebook_url': forms.URLInput(attrs={'placeholder': 'https://facebook.com/your-page'}),
            'website_url': forms.URLInput(attrs={'placeholder': 'https://yourwebsite.com'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['username'].initial = self.user.username
        self.fields['first_name'].initial = self.user.first_name
        self.fields['last_name'].initial = self.user.last_name
        self.fields['email'].initial = self.user.email

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("A user with this email address already exists.")
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = self.user
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            profile.save()
        return profile
