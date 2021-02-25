from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('run', views.RunSimulationView.as_view(), name='runSimulation'),
    #path('transform', views.TransformView)
]
