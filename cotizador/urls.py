# cotizador/urls.py

from django.urls import path
from . import views  # <-- Ya estamos importando el archivo views.py

urlpatterns = [
    # 1. La ruta que ya teníamos para la cotización del cliente
    path('cotizacion/<uuid:id_unico>/', views.vista_cotizacion, name='vista_cotizacion'),

    # 2. ¡NUEVA RUTA! Esta es la que usará el JavaScript
    path('get_precio_producto/<int:producto_id>/', views.get_precio_producto, name='get_precio_producto'),
]