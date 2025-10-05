from django.contrib import admin
from .models import (
    Proveedor,
    Producto,
    Intermediario,
    Cliente,
    Proyecto,
    DetalleItemProyecto,
    Cotizacion,
    ItemCotizacion,
)

# Esta clase define cómo se mostrarán los detalles DENTRO de un Proyecto
class DetalleItemProyectoInline(admin.TabularInline):
    model = DetalleItemProyecto
    extra = 1 # Muestra un espacio en blanco para agregar un nuevo detalle fácilmente

# Esta clase personaliza la vista del modelo Proyecto
class ProyectoAdmin(admin.ModelAdmin):
    inlines = [DetalleItemProyectoInline] # Aquí conectamos los detalles con el proyecto
    list_display = ('nombre', 'cliente', 'estado', 'fecha_creacion') # Columnas que se verán en la lista de proyectos
    list_filter = ('estado', 'cliente') # Agrega filtros en la barra lateral

# --- Registramos los modelos de nuevo, pero con la nueva configuración ---

# Modelos simples que no necesitan personalización por ahora
admin.site.register(Proveedor)
admin.site.register(Producto)
admin.site.register(Intermediario)
admin.site.register(Cliente)
admin.site.register(Cotizacion)
admin.site.register(ItemCotizacion)

# Registramos el modelo Proyecto usando nuestra clase personalizada
admin.site.register(Proyecto, ProyectoAdmin)