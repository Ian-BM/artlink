from django.db import models
from django.contrib.auth.models import User
import uuid

class Artwork(models.Model):
    MEDIUM_CHOICES = [
        ('oil', 'Oil'),
        ('acrylic', 'Acrylic'),
        ('watercolor', 'Watercolor'),
        ('mixed', 'Mixed Media'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    medium = models.CharField(max_length=20, choices=MEDIUM_CHOICES)
    size = models.CharField(max_length=100)  # e.g., "24x30 inches"
    year_created = models.PositiveIntegerField()
    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='artworks')
    images = models.ImageField(upload_to='artworks/', blank=True, null=True)  # For simplicity, one image; can add more
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Certificate(models.Model):
    certificate_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    artwork = models.OneToOneField(Artwork, on_delete=models.CASCADE, related_name='certificate')
    certificate_pdf = models.FileField(upload_to='certificates/', blank=True, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate {self.certificate_id} for {self.artwork.title}"
