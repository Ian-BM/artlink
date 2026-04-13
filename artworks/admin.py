from django.contrib import admin
from .models import Artwork, Certificate

@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'price', 'status', 'year_created')
    list_filter = ('status', 'medium', 'year_created')
    search_fields = ('title', 'artist__username', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'artwork', 'issued_at')
    search_fields = ('certificate_id', 'artwork__title')
