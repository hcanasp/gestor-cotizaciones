# cotizador/admin.py

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
    Contacto,
    ResponsabilidadFiscal,
    HitoPago,
    Remision,
    ItemRemision,
)

class ContactoInline(admin.TabularInline):
    model = Contacto
    extra = 1 

class DetalleItemProyectoInline(admin.TabularInline):
    model = DetalleItemProyecto
    extra = 1

class ProyectoAdmin(admin.ModelAdmin):
    inlines = [DetalleItemProyectoInline]
    list_display = ('nombre', 'cliente', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'cliente')
    search_fields = ['nombre', 'cliente__nombres', 'cliente__razon_social']
    class Media:
        js = ('cotizador/autocomplete_precio.js',)

class HitoPagoInline(admin.TabularInline):
    model = HitoPago
    extra = 1 
    fields = ('porcentaje', 'descripcion', 'valor') 
    readonly_fields = ('valor',)    

class CotizacionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'proyecto', 'version', 'total', 'id_unico')
    readonly_fields = ('id_unico',)
    inlines = [HitoPagoInline]

    class Media:
        js = ('cotizador/cotizacion_admin.js',)
        css = {
            'all': ('cotizador/cotizacion_admin.css',) # Esto es opcional, pero ayuda a forzar la carga
        }
    
class ClienteAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Datos Básicos', {
            'fields': ('tipo',)
        }),
        ('Información de Persona', {
            'classes': ('persona-fields',), # Clase para futuro JS
            'fields': ('nombres', 'apellidos')
        }),
        ('Información de Empresa', {
            'classes': ('empresa-fields',), # Clase para futuro JS
            'fields': ('razon_social', 'nombre_comercial')
        }),
        ('Identificación y Contacto', {
            'fields': ('tipo_identificacion', 'identificacion', 'digito_verificacion', 'email', 'telefono', 'direccion', 'ciudad')
        }),
        ('Información Fiscal', {
            'fields': ('responsabilidades_fiscales',)
        }),
    ]
    
    inlines = [ContactoInline]

    filter_horizontal = ('responsabilidades_fiscales',)

    list_display = ('__str__', 'tipo', 'identificacion', 'email')
    list_filter = ('tipo', 'ciudad')

    

# --- Registros ---
admin.site.register(Proveedor)
admin.site.register(Intermediario)
admin.site.register(Cliente, ClienteAdmin) 
admin.site.register(ItemCotizacion)
admin.site.register(Proyecto, ProyectoAdmin)
admin.site.register(ResponsabilidadFiscal)
admin.site.register(Contacto)
admin.site.register(Cotizacion, CotizacionAdmin)

# --- Configuración para Remisiones ---

class ItemRemisionInline(admin.TabularInline):
    model = ItemRemision
    extra = 1
    autocomplete_fields = ['producto']

class RemisionAdmin(admin.ModelAdmin):
    inlines = [ItemRemisionInline]
    list_display = ('id', 'proyecto', 'fecha_creacion', 'recibido_por')
    list_filter = ('fecha_creacion',)
    search_fields = ['proyecto__nombre', 'recibido_por']
    autocomplete_fields = ['proyecto']

admin.site.register(Remision, RemisionAdmin)

# Modificación a ProductoAdmin para permitir búsqueda
class ProductoAdmin(admin.ModelAdmin):
    search_fields = ['nombre']

# Re-registramos Producto con la nueva configuración
admin.site.register(Producto, ProductoAdmin)