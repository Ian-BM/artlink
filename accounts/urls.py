from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.RoleBasedLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_choice, name='register'),
    path('register/buyer/', views.register_buyer, name='register_buyer'),
    path('register/artist/', views.register_artist, name='register_artist'),
    path('artist/profile/edit/', views.edit_artist_profile, name='edit_artist_profile'),
]
