from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('callback/', views.payment_callback, name='callback'),
]