from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils.text import slugify

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


class Exhibition(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    cover_image = models.ImageField(upload_to='exhibitions/', blank=True, null=True)
    description = models.TextField()
    curator_name = models.CharField(max_length=150)
    start_date = models.DateField()
    end_date = models.DateField()
    artworks = models.ManyToManyField(Artwork, related_name='exhibitions', blank=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-featured', '-start_date', 'title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'exhibition'
            slug = base_slug
            counter = 2
            while Exhibition.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
