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
