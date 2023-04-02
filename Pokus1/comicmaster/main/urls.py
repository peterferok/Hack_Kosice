from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('images/', views.ImagesView.as_view(), name='images')
]
