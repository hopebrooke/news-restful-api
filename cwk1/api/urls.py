from django.contrib import admin
from django.urls import path

from api.views import handleLogin, handleLogout, stories, delete

urlpatterns = [
    path('login', handleLogin),
    path('logout', handleLogout),
    path('stories', stories),
    path('stories/', stories),
    path('stories/<int:id>', delete),
]