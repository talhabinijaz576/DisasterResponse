from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('start', views.StartEvacuationView, name='start'),
    path('view', views.EvacuationHistoryView, name='history'),
]
