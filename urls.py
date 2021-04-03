"""Assign URL paths to views for timelesstravel scavenger hunt
"""
from django.urls import path
from . import views

urlpatterns = [
    path('random_number', views.get_random_number, name="random_number"),
    path('', views.index_view, name='index'),
]
