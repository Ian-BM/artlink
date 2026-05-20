from django import forms
from django.core.validators import FileExtensionValidator
from artworks.models import Artwork, Certificate
from dashboard.models import Inquiry

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