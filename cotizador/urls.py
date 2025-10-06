# cotizador/urls.py

from django.urls import path
from . import views # Pronto importaremos nuestras vistas aquí

urlpatterns = [
    # Aquí definiremos la ruta para ver una cotización.
    path('cotizacion/<uuid:id_unico>/', views.vista_cotizacion, name='vista_cotizacion'),
]