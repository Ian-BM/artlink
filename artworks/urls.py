from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('artwork/<int:pk>/', views.artwork_detail, name='artwork_detail'),
    path('artist_profile/<int:pk>/', views.artist_profile, name='artist_profile'),
    path('artists/', views.artists_list, name='artists'),
    path('verify/', views.verify_certificate, name='verify_certificate'),
]