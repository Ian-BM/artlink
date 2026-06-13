from django import forms
from django.core.validators import FileExtensionValidator
from artworks.models import Artwork, Certificate, Exhibition
from dashboard.models import Inquiry, CustomArtworkRequest

class ArtworkForm(forms.ModelForm):
    # Restrict certificate uploads to PDFs only to reduce unsafe file handling.
    certificate_pdf = forms.FileField(
        required=False,
        label='Certificate of Authenticity (PDF)',
        help_text='Upload a PDF file for the certificate',
        validators=[FileExtensionValidator(['pdf'])],
    )
    
    class Meta:
        model = Artwork
        fields = ['title', 'description', 'price', 'medium', 'size', 'year_created', 'images']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Describe your artwork, its inspiration, and details...'}),
            'title': forms.TextInput(attrs={'placeholder': 'Artwork title'}),
        }

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Send a message to the artist...'}),
        }


class CustomArtworkRequestForm(forms.ModelForm):
    reference_image = forms.ImageField(
        required=False,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])],
        label='Reference Image',
    )

    class Meta:
        model = CustomArtworkRequest
        fields = [
            'buyer_name',
            'buyer_email',
            'buyer_whatsapp',
            'artwork_type',
            'budget',
            'deadline',
            'description',
            'reference_image',
        ]
        widgets = {
            'buyer_name': forms.TextInput(attrs={'placeholder': 'Your full name'}),
            'buyer_email': forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
            'buyer_whatsapp': forms.TextInput(attrs={'placeholder': '+254 700 000 000'}),
            'budget': forms.NumberInput(attrs={'placeholder': '500', 'step': '0.01'}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Describe the artwork, preferred style, size, colors, story, and any must-have details...'}),
        }
        labels = {
            'buyer_name': 'Name',
            'buyer_email': 'Email',
            'buyer_whatsapp': 'WhatsApp Number',
            'artwork_type': 'Artwork Type',
            'budget': 'Budget',
            'deadline': 'Deadline',
            'description': 'Description',
            'reference_image': 'Reference Image Upload',
        }


class CustomArtworkRequestStatusForm(forms.ModelForm):
    class Meta:
        model = CustomArtworkRequest
        fields = ['status']


class ExhibitionForm(forms.ModelForm):
    artworks = forms.ModelMultipleChoiceField(
        queryset=Artwork.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Select Artworks',
    )

    class Meta:
        model = Exhibition
        fields = [
            'title',
            'slug',
            'cover_image',
            'description',
            'curator_statement',
            'start_date',
            'end_date',
            'featured_image',
            'visibility',
            'artworks',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Exhibition title'}),
            'slug': forms.TextInput(attrs={'placeholder': 'exhibition-slug'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Exhibition overview for visitors...'}),
            'curator_statement': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Your curatorial vision and narrative...'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, artist=None, **kwargs):
        super().__init__(*args, **kwargs)
        if artist is not None:
            self.fields['artworks'].queryset = Artwork.objects.filter(artist=artist).order_by('-created_at')

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError('End date must be on or after the start date.')
        return cleaned_data
