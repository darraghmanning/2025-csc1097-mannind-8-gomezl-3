from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_pdf, name='upload_pdf'),
    path('auth/google/', views.GoogleLoginView.as_view(), name="google-auth"),
]