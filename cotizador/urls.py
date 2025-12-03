# cotizador/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Rutas para el cliente (Documentos)
    path('cotizacion/<uuid:id_unico>/', views.vista_cotizacion, name='vista_cotizacion'),
    path('remision/<int:remision_id>/', views.vista_remision, name='vista_remision'),

    # Rutas para el sistema interno (APIs)
    path('get_precio_producto/<int:producto_id>/', views.get_precio_producto, name='get_precio_producto'),
    path('get_trm_actual/', views.get_trm_actual, name='get_trm_actual'),
]