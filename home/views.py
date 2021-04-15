from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from pprint import pprint

@login_required(login_url="/accounts/login/")
def index(request):

    if(request.user.is_superuser):
        return redirect('/admin/')
    if(request.user.user_type=="CONTROLROOM"):
        return redirect('/controlroom/startSimulation')
    else:
        return redirect('/accounts/login/')

    