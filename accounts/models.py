from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    USER_TYPE_CHOICES = [
        ('artist', 'Artist'),
        ('buyer', 'Buyer'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    # For artists
    total_artworks_sold = models.PositiveIntegerField(default=0)
    certifications = models.TextField(blank=True)  # JSON or text for badges
    artist_statement = models.TextField(blank=True)
    instagram_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"
