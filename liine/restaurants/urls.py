from django.urls import path

from restaurants import views

urlpatterns = [
  path('', views.home, name="home"),
  path('search/', views.search, name="search")
]