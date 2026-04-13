from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'location', 'total_artworks_sold')
    list_filter = ('user_type',)
    search_fields = ('user__username', 'location')
