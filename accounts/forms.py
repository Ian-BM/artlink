from django import forms
from django.contrib.auth.models import User
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
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        country_code = cleaned_data.get('country_code')
        phone_number = cleaned_data.get('phone_number')

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
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        return cleaned_data

class ArtistRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Password")
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True, label="Confirm Password")
    email = forms.EmailField(required=True)
    profile_picture = forms.ImageField(required=False, label="Profile Picture")

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        username = cleaned_data.get('username')

        if not username:
            raise forms.ValidationError("Username is required.")
        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        
        return cleaned_data
