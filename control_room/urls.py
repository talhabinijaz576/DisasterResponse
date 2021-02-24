from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('home', views.ControlRoomHomeView, name='index'),
    path('startSimulation', views.StartSimulation, name='startSimulation'),
    #path('transform', views.TransformView)
]
