from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('hospitals', views.ManagerView, name='hospitals'),
    path('policestations', views.ManagerView, name='policestations'),
    path('firestations', views.ManagerView, name='firestations'),
    #path('transform', views.TransformView)
]
