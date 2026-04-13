from django.contrib import admin
from .models import Inquiry

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'artwork', 'created_at', 'replied')
    list_filter = ('replied', 'created_at')
    search_fields = ('buyer__username', 'artwork__title', 'message')
