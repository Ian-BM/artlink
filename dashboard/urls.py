from django.urls import path
from . import views

urlpatterns = [
    path('', views.artist_dashboard, name='dashboard'),
    path('artworks/', views.dashboard_artworks, name='dashboard_artworks'),
    path('sales/', views.dashboard_sales, name='dashboard_sales'),
    path('upload/', views.upload_artwork, name='upload_artwork'),
    path('artwork/<int:artwork_id>/edit/', views.edit_artwork, name='edit_artwork'),
    path('artwork/<int:artwork_id>/delete/', views.delete_artwork, name='delete_artwork'),
    path('artwork/<int:artwork_id>/status/', views.toggle_artwork_status, name='toggle_artwork_status'),
    path('inquiries/', views.inquiry_inbox, name='inquiry_inbox'),
    path('custom-requests/', views.custom_request_inbox, name='custom_request_inbox'),
    path('custom-requests/<int:request_id>/status/', views.update_custom_request_status, name='update_custom_request_status'),
    path('exhibitions/', views.dashboard_exhibitions, name='dashboard_exhibitions'),
    path('exhibitions/create/', views.create_exhibition, name='create_exhibition'),
    path('exhibitions/<int:exhibition_id>/edit/', views.edit_exhibition, name='edit_exhibition'),
    path('exhibitions/<int:exhibition_id>/delete/', views.delete_exhibition, name='delete_exhibition'),
    path('exhibitions/<int:exhibition_id>/visibility/', views.toggle_exhibition_visibility, name='toggle_exhibition_visibility'),
    path('inquiry/<int:artwork_id>/', views.send_inquiry, name='send_inquiry'),
]
