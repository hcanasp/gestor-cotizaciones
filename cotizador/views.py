# cotizador/views.py

from django.shortcuts import render, get_object_or_404
from .models import Cotizacion

def vista_cotizacion(request, id_unico):
    """
    Esta función busca una cotización por su ID único y la muestra.
    """
    # Usamos get_object_or_404 para buscar la cotización.
    # Si no la encuentra, automáticamente mostrará una página de error 404.
    cotizacion = get_object_or_404(Cotizacion, id_unico=id_unico)

    # Por ahora, simplemente imprimiremos el resultado en la terminal.
    # Más adelante, aquí le diremos a Django que muestre un archivo HTML.
    print(f"Se encontró la cotización para: {cotizacion.proyecto.cliente.nombre}")
    print(f"Total: {cotizacion.total}")

    # Aquí es donde le pasaremos los datos a una plantilla HTML.
    # Lo dejaremos pendiente para el siguiente paso.
    contexto = {
        'cotizacion': cotizacion,
    }

    return render(request, 'cotizador/vista_cotizacion.html', contexto) 
