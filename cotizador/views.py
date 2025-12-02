# cotizador/views.py

from django.shortcuts import render, get_object_or_404
from .models import Cotizacion, Producto  # <-- Asegúrate de que 'Producto' esté aquí
from django.http import JsonResponse      # <-- Añade esta línea

def vista_cotizacion(request, id_unico):
    """
    Esta función busca una cotización por su ID único y la muestra.
    """
    # Usamos get_object_or_404 para buscar la cotización.
    # Si no la encuentra, automáticamente mostrará una página de error 404.
    cotizacion = get_object_or_404(Cotizacion, id_unico=id_unico)

        # Aquí es donde le pasaremos los datos a una plantilla HTML.
    # Lo dejaremos pendiente para el siguiente paso.
    contexto = {
        'cotizacion': cotizacion,
    }

    return render(request, 'cotizador/vista_cotizacion.html', contexto)

# --- VISTA 2: NUESTRA "MINI-API" PARA OBTENER PRECIOS ---
def get_precio_producto(request, producto_id):
    """
    Esta vista busca un producto por su ID y devuelve
    su precio_venta_final y garantia en formato JSON.
    """
    try:
        # Buscamos el producto en la base de datos
        producto = Producto.objects.get(id=producto_id)

        # Devolvemos ambos datos
        data = {
            'precio': str(producto.precio_venta_final),
            'garantia': producto.garantia_default_meses,
        }
        return JsonResponse(data)

    except Producto.DoesNotExist:
        # Si el producto no existe, devolvemos un error
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
