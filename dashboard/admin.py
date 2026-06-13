from django.contrib import admin
from .models import Inquiry, CustomArtworkRequest

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'artwork', 'created_at', 'replied')
    list_filter = ('replied', 'created_at')
    search_fields = ('buyer__username', 'artwork__title', 'message')


@admin.register(CustomArtworkRequest)
class CustomArtworkRequestAdmin(admin.ModelAdmin):
    list_display = ('buyer_name', 'artist', 'artwork_type', 'budget', 'status', 'created_at')
    list_filter = ('status', 'artwork_type', 'created_at')
    search_fields = ('buyer_name', 'buyer_email', 'artist__username', 'description')
    readonly_fields = ('created_at',)
