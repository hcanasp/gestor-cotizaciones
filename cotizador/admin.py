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
    class Media:
        js = ('cotizador/autocomplete_precio.js',)

class HitoPagoInline(admin.TabularInline):
    model = HitoPago
    extra = 1 
    fields = ('porcentaje', 'descripcion', 'valor') 
    readonly_fields = ('valor',)    

class CotizacionAdmin(admin.ModelAdmin):
    inlines = [HitoPagoInline]
    list_display = ('__str__', 'proyecto', 'version', 'total', 'id_unico')
    readonly_fields = ('id_unico',)
    
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
admin.site.register(Producto)
admin.site.register(Intermediario)
admin.site.register(Cliente, ClienteAdmin) 
admin.site.register(ItemCotizacion)
admin.site.register(Proyecto, ProyectoAdmin)
admin.site.register(ResponsabilidadFiscal)
admin.site.register(Contacto)
admin.site.register(Cotizacion, CotizacionAdmin)