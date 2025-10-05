# Importaciones necesarias de Django
from django.db import models
from django.utils import timezone
import uuid

# --- MODELOS DE SOPORTE ---

class Proveedor(models.Model):
    nombre = models.CharField(max_length=200)
    contacto = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    def __str__(self): return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    costo_adquisicion = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    precio_venta_final = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    def __str__(self): return self.nombre

class Intermediario(models.Model):
    nombre_completo = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    datos_pago = models.TextField(blank=True, help_text="Información para liquidación de comisiones")
    def __str__(self): return self.nombre_completo

class Cliente(models.Model):
    nombre = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    def __str__(self): return self.nombre

# --- MODELOS CENTRALES DEL FLUJO DE TRABAJO ---

class Proyecto(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255, help_text="Ej: Remodelación Apartamento 701")
    fecha_creacion = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=50, default='En Diseño')
    intermediario = models.ForeignKey(Intermediario, on_delete=models.SET_NULL, null=True, blank=True)
    porcentaje_comision_interna = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    valor_comision_calculada = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    estado_comision = models.CharField(max_length=50, default='PENDIENTE')
    def __str__(self): return self.nombre

class DetalleItemProyecto(models.Model):
    proyecto = models.ForeignKey(Proyecto, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)
    descripcion_manual = models.CharField(max_length=255, blank=True)
    precio_unitario_capturado = models.DecimalField(max_digits=10, decimal_places=2)
    espacio = models.CharField(max_length=200, help_text="Ej: Cocina")
    sub_espacio = models.CharField(max_length=200, blank=True, help_text="Ej: Isla Central")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    color_carcaza = models.CharField(max_length=100, blank=True)
    def __str__(self): return f"Detalle para {self.proyecto.nombre}"

# Sigue estando en el archivo cotizador/models.py

class Cotizacion(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    version = models.PositiveIntegerField(default=1)
    es_activa = models.BooleanField(default=True)
    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    valida_hasta = models.DateField()
    subtotal_antes_impuestos = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    porcentaje_impuestos = models.DecimalField(max_digits=5, decimal_places=2, default=19.00)
    valor_impuestos_calculado = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mostrar_impuestos_desglosados = models.BooleanField(default=False)
    condiciones_comerciales = models.TextField(blank=True)
    tiempos_entrega = models.TextField(blank=True)
    garantia = models.TextField(blank=True)

    # --- ¡ESTA ES LA NUEVA LÓGICA (EL MOTOR)! ---
    def save(self, *args, **kwargs):
        # 1. Agrupar y sumar los detalles del proyecto.
        #    Usamos un diccionario para guardar los totales de cada producto.
        resumen_productos = {}
        
        #    Recorremos cada detalle del proyecto asociado a esta cotización.
        for detalle in self.proyecto.detalles.all():
            #    Si es un producto del inventario, usamos su ID como clave.
            if detalle.producto:
                clave = detalle.producto.id
                descripcion = detalle.producto.nombre
                precio = detalle.precio_unitario_capturado
            #    Si es un servicio manual, usamos su descripción como clave.
            else:
                clave = detalle.descripcion_manual
                descripcion = detalle.descripcion_manual
                precio = detalle.precio_unitario_capturado

            if clave not in resumen_productos:
                resumen_productos[clave] = {
                    'producto_obj': detalle.producto, # Guardamos el objeto producto
                    'descripcion': descripcion,
                    'cantidad_total': 0,
                    'precio_unitario': precio
                }
            
            resumen_productos[clave]['cantidad_total'] += detalle.cantidad

        # 2. Calcular los totales de la cotización.
        subtotal = sum(item['cantidad_total'] * item['precio_unitario'] for item in resumen_productos.values())
        impuestos = subtotal * (self.porcentaje_impuestos / 100)
        
        self.subtotal_antes_impuestos = subtotal
        self.valor_impuestos_calculado = impuestos
        self.total = subtotal + impuestos

        # 3. Guardamos la cotización con los nuevos totales calculados.
        #    El 'super().save()' es la forma de llamar al guardado original de Django.
        super().save(*args, **kwargs)

        # 4. Limpiamos los items antiguos y creamos los nuevos items resumidos.
        self.items.all().delete() # Borramos los items de la versión anterior para no duplicar

        for clave, data in resumen_productos.items():
            ItemCotizacion.objects.create(
                cotizacion=self,
                producto=data['producto_obj'],
                descripcion_agrupada=data['descripcion'],
                cantidad=data['cantidad_total'],
                precio_unitario=data['precio_unitario']
            )

    def __str__(self):
        return f"Cotización V{self.version} para: {self.proyecto.nombre}"

class ItemCotizacion(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)
    descripcion_agrupada = models.CharField(max_length=255)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    def subtotal(self): return self.cantidad * self.precio_unitario
    def __str__(self): return f"Resumen: {self.cantidad} x {self.descripcion_agrupada}"