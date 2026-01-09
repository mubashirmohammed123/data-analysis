from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('upload/', views.upload_view, name='upload_view'),
    path('generate-pdf/', views.generate_pdf, name='generate_pdf'),
    
]