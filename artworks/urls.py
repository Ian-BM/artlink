from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('artwork/<int:pk>/', views.artwork_detail, name='artwork_detail'),
    path('artist_profile/<int:pk>/', views.artist_profile, name='artist_profile'),
    path('artists/', views.artists_list, name='artists'),
    path('verify/', views.verify_certificate, name='verify_certificate'),
    path('exhibitions/', views.exhibitions_home, name='exhibitions'),
    path('exhibitions/<slug:slug>/', views.exhibition_detail, name='exhibition_detail'),
    path('exhibitions/<slug:slug>/gallery/', views.exhibition_gallery, name='exhibition_gallery'),
]
