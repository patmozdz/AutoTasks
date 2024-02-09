from django.urls import path
from .api_views import discord_webhook

urlpatterns = [
    path('discord_webhook/', discord_webhook, name='discord_webhook'),
]
