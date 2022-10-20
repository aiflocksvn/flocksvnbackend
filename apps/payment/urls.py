from django.urls import path
from rest_framework.routers import SimpleRouter
from .api import TransactionEvent, CryptoTransactionEvent

urlpatterns = [
    path('transacion_event/', TransactionEvent.as_view()),
    path('transacion_event/binance/', CryptoTransactionEvent.as_view())
]
