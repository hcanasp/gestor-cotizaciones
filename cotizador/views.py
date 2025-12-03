# cotizador/views.py

from django.shortcuts import render, get_object_or_404
from .models import Cotizacion, Producto, Remision  # <-- Asegúrate de que 'Producto' esté aquí
from django.http import JsonResponse      # <-- Añade esta línea
import requests


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

# --- VISTA 3: OBTENER TRM ACTUAL (MOCK) ---
# --- VISTA 3: OBTENER TRM ACTUAL (REAL) ---
def get_trm_actual(request):
    """
    Retorna la TRM actual consultando la API externa.
    """
    # Usamos una API pública y gratuita de tasas de cambio
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data_api = response.json()
            # La API devuelve: {"rates": {"COP": 4123.45, ...}, ...}
            trm_valor = data_api.get('rates', {}).get('COP')
            
            if trm_valor:
                return JsonResponse({'trm': trm_valor})
            else:
                return JsonResponse({'error': 'No se encontró la tasa COP en la respuesta'}, status=500)
        else:
            return JsonResponse({'error': 'Error al consultar la API externa'}, status=500)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
from django.shortcuts import render, get_object_or_404

def vista_remision(request, remision_id):
    """
    Vista para visualizar una Remisión específica.
    """
    remision = get_object_or_404(Remision, pk=remision_id)
    return render(request, 'cotizador/vista_remision.html', {'remision': remision})
