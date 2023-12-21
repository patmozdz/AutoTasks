from django.urls import path
from .views import sms_response

urlpatterns = [
    path('sms/', sms_response, name='sms_response'),
]
