from django.urls import path
from . import views

urlpatterns = [
    path('', views.artist_dashboard, name='dashboard'),
    path('upload/', views.upload_artwork, name='upload_artwork'),
    path('artwork/<int:artwork_id>/edit/', views.edit_artwork, name='edit_artwork'),
    path('artwork/<int:artwork_id>/delete/', views.delete_artwork, name='delete_artwork'),
    path('artwork/<int:artwork_id>/status/', views.toggle_artwork_status, name='toggle_artwork_status'),
    path('inquiries/', views.inquiry_inbox, name='inquiry_inbox'),
    path('custom-requests/', views.custom_request_inbox, name='custom_request_inbox'),
    path('custom-requests/<int:request_id>/status/', views.update_custom_request_status, name='update_custom_request_status'),
    path('inquiry/<int:artwork_id>/', views.send_inquiry, name='send_inquiry'),
]
