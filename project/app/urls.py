from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('author/', views.author, name='author'),
    path('spec/', views.spec_list, name='spec_list'),
    path('spec/<int:id>/', views.spec_detail, name='spec_detail'),
    path('404/', views.error_404, name='error_404'),
]