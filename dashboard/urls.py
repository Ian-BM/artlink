from django.urls import path
from . import views

urlpatterns = [
    path('', views.artist_dashboard, name='dashboard'),
    path('upload/', views.upload_artwork, name='upload_artwork'),
    path('inquiries/', views.inquiry_inbox, name='inquiry_inbox'),
    path('inquiry/<int:artwork_id>/', views.send_inquiry, name='send_inquiry'),
]