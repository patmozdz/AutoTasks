from django.urls import path
from .api_views import receive_sms_from_twilio

urlpatterns = [
    path('twilio_endpoint/', receive_sms_from_twilio, name='twilio_endpoint'),
]
