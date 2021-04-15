from django.contrib import admin
from django.urls import path
from evacuation_manager.views import DisasterHistoryView
from . import views

urlpatterns = [
    path('hospitals', views.ManagerView, name='hospitals'),
    path('policestations', views.ManagerView, name='policestations'),
    path('firestations', views.ManagerView, name='firestations'),
    path('evacuationpoints', views.ManagerView, name='evacuationpoints'),
    path('disasters', DisasterHistoryView, name='history'),
    #path('transform', views.TransformView)
]
