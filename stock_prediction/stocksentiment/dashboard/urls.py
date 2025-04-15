from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('historic/', views.historic, name='historic'),
    path('live/', views.live, name='live'),
    path('correlation/', views.correlation_view, name='correlation'),
]
