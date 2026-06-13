from django.db import models
from django.contrib.auth.models import User
from artworks.models import Artwork

class Inquiry(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inquiries_sent')
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name='inquiries')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    replied = models.BooleanField(default=False)

    def __str__(self):
        return f"Inquiry from {self.buyer.username} for {self.artwork.title}"


class CustomArtworkRequest(models.Model):
    ARTWORK_TYPE_CHOICES = [
        ('portrait', 'Portrait'),
        ('family_portrait', 'Family Portrait'),
        ('pet_portrait', 'Pet Portrait'),
        ('landscape', 'Landscape'),
        ('abstract', 'Abstract'),
        ('character_art', 'Character Art'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('completed', 'Completed'),
        ('declined', 'Declined'),
    ]

    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_artwork_requests')
    buyer_name = models.CharField(max_length=150)
    buyer_email = models.EmailField()
    buyer_whatsapp = models.CharField(max_length=30, blank=True)
    artwork_type = models.CharField(max_length=30, choices=ARTWORK_TYPE_CHOICES)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateField(blank=True, null=True)
    description = models.TextField()
    reference_image = models.ImageField(upload_to='custom_requests/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.buyer_name} request for {self.artist.username}"

    @property
    def whatsapp_url(self):
        digits = ''.join(character for character in self.buyer_whatsapp if character.isdigit())
        if not digits:
            return ''
        return f"https://wa.me/{digits}"
