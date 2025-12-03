# Importaciones necesarias de Django
from django.core.validators import RegexValidator
from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid

# --- MODELOS DE SOPORTE ---

class Proveedor(models.Model):
    # --- Campos para diferenciar Persona y Empresa ---
    TIPO_PROVEEDOR_CHOICES = [
        ('PERSONA', 'Persona'),
        ('EMPRESA', 'Empresa'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPO_PROVEEDOR_CHOICES, default='EMPRESA')

    # --- Campos para Persona ---
    nombres = models.CharField(max_length=200, blank=True)
    apellidos = models.CharField(max_length=200, blank=True)

    # --- Campos para Empresa ---
    razon_social = models.CharField(max_length=255, blank=True)
    nombre_comercial = models.CharField(max_length=255, blank=True)

    # --- Campos Comunes de Identificación ---
    TIPO_ID_CHOICES = [
        ('NIT', 'NIT'),
        ('CC', 'Cédula de ciudadanía'),
    ]
    tipo_identificacion = models.CharField(max_length=5, choices=TIPO_ID_CHOICES, blank=True)
    identificacion = models.CharField(max_length=20, blank=True, unique=True, null=True)
    digito_verificacion = models.CharField("DV", max_length=1, blank=True)

    # --- Campos Comunes de Contacto y Ubicación ---
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)

    # --- Campos Fiscales ---
    responsabilidades_fiscales = models.ManyToManyField('ResponsabilidadFiscal', blank=True)

    def __str__(self):
        if self.tipo == 'PERSONA':
            return f"{self.nombres} {self.apellidos}"
        return self.razon_social or self.nombre_comercial or "Proveedor sin nombre"

class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    costo_adquisicion = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    precio_venta_final = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    stock_actual = models.PositiveIntegerField(default=0) # --- ¡NUEVO CAMPO PARA EL INVENTARIO! ---
    garantia_default_meses = models.PositiveIntegerField("Garantía (meses)", default=12)
    def __str__(self): return self.nombre

class Intermediario(models.Model):
    nombre_completo = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    datos_pago = models.TextField(blank=True, help_text="Información para liquidación de comisiones")
    def __str__(self): return self.nombre_completo

    # ¡NUEVO MODELO para las opciones de Responsabilidad Fiscal!
class ResponsabilidadFiscal(models.Model):
    codigo = models.CharField(max_length=5)
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

# ¡NUEVO MODELO para los contactos adicionales!
class Contacto(models.Model):
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, related_name='contactos')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    cargo = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# ¡MODELO CLIENTE ACTUALIZADO Y MEJORADO!
class Cliente(models.Model):

    # --- Campos para diferenciar Persona y Empresa ---
    TIPO_CLIENTE_CHOICES = [
        ('PERSONA', 'Persona'),
        ('EMPRESA', 'Empresa'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPO_CLIENTE_CHOICES, default='PERSONA')

    # --- Campos para Persona ---
    nombres = models.CharField(max_length=200, blank=True)
    apellidos = models.CharField(max_length=200, blank=True)

    # --- Campos para Empresa ---
    razon_social = models.CharField(max_length=255, blank=True)
    nombre_comercial = models.CharField(max_length=255, blank=True)

    # --- Campos Comunes de Identificación ---
    TIPO_ID_CHOICES = [
        ('NIT', 'NIT'),
        ('CC', 'Cédula de ciudadanía'),
    ]
    tipo_identificacion = models.CharField(max_length=5, choices=TIPO_ID_CHOICES, blank=True)
    identificacion = models.CharField(max_length=20, blank=True, unique=True, null=True)
    digito_verificacion = models.CharField("DV", max_length=1, blank=True)

    # --- Campos Comunes de Contacto y Ubicación ---
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)

    # --- Campos Fiscales ---
    responsabilidades_fiscales = models.ManyToManyField(ResponsabilidadFiscal, blank=True)

    def __str__(self):
        if self.tipo == 'PERSONA':
            return f"{self.nombres} {self.apellidos}"
        else:
            return self.razon_social
        
# --- CLASE PROYECTO ACTUALIZADA CON LÓGICA DE INVENTARIO ---
class Proyecto(models.Model):
    
    # --- ¡NUEVO! Opciones para el estado ---
    ESTADO_CHOICES = [
        ('DISEÑO', 'En Diseño'),
        ('COTIZADO', 'Cotizado'),
        ('APROBADO', 'Aprobado'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255, help_text="Ej: Remodelación Apartamento 701")
    fecha_creacion = models.DateTimeField(default=timezone.now)
    
    # --- ¡CAMBIO! Ahora usa el menú desplegable ---
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='DISEÑO') 
    
    intermediario = models.ForeignKey(Intermediario, on_delete=models.SET_NULL, null=True, blank=True)
    porcentaje_comision_interna = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    valor_comision_calculada = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    estado_comision = models.CharField(max_length=50, default='PENDIENTE')

    def __str__(self): 
        return self.nombre

    # --- ¡NUEVO! LÓGICA PARA EL INVENTARIO ---
    def save(self, *args, **kwargs):
        # Variable para saber si debemos procesar el inventario
        descontar_stock = False
        
        # Primero, revisamos si el proyecto ya existe (self.pk)
        if self.pk:
            try:
                # Traemos la versión "antigua" del proyecto desde la BD
                proyecto_anterior = Proyecto.objects.get(pk=self.pk)
                
                # Comparamos el estado anterior con el nuevo
                if self.estado == 'APROBADO' and proyecto_anterior.estado != 'APROBADO':
                    # ¡Este es el momento exacto! Acaba de cambiar a APROBADO.
                    descontar_stock = True
            except Proyecto.DoesNotExist:
                pass # Es un proyecto nuevo, no hay nada que comparar

        # Si marcamos que sí debemos descontar...
        if descontar_stock:
            try:
                # Usamos 'transaction.atomic' para seguridad:
                # Si falla un solo producto, no se descuenta NINGUNO.
                with transaction.atomic():
                    # Recorremos cada producto en el detalle del proyecto
                    for detalle in self.detalles.all():
                        # Solo si es un producto (no un servicio manual)
                        if detalle.producto:
                            producto = detalle.producto
                            
                            # Verificamos si hay stock suficiente
                            if producto.stock_actual < detalle.cantidad:
                                # Si no hay, detenemos todo y lanzamos un error
                                raise ValidationError(
                                    f"No hay stock suficiente para '{producto.nombre}'. "
                                    f"Stock actual: {producto.stock_actual}, se necesitan: {detalle.cantidad}"
                                )
                            
                            # Si hay stock, lo descontamos
                            # OJO: Convertimos la cantidad (Decimal) a entero (int)
                            producto.stock_actual -= int(detalle.cantidad)
                            producto.save() # Guardamos el producto con el nuevo stock

            except ValidationError as e:
                # Si hubo un error (como falta de stock), no guardamos el cambio
                # de estado y le mostramos el error al usuario en el admin.
                # Para hacer esto, simplemente relanzamos el error.
                raise e

        # Finalmente, guardamos el proyecto (con su nuevo estado 'APROBADO')
        super().save(*args, **kwargs)

class DetalleItemProyecto(models.Model):
    proyecto = models.ForeignKey(Proyecto, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)
    descripcion_manual = models.CharField(max_length=255, blank=True)
    precio_unitario_capturado = models.DecimalField(max_digits=10, decimal_places=2)
    espacio = models.CharField(max_length=200, help_text="Ej: Cocina")
    sub_espacio = models.CharField(max_length=200, blank=True, help_text="Ej: Isla Central")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    color_carcaza = models.CharField(max_length=100, blank=True)
    garantia_especifica_meses = models.PositiveIntegerField("Garantía (meses)", blank=True, null=True) # --- ¡NUEVO CAMPO PARA GARANTÍA ESPECÍFICA! ---
    def __str__(self): return f"Detalle para {self.proyecto.nombre}"

class HitoPago(models.Model):
    cotizacion = models.ForeignKey('Cotizacion', related_name='pagos', on_delete=models.CASCADE)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, help_text="Ej: 50 para 50%")
    valor = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    descripcion = models.CharField(max_length=255)
    fecha_pago = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.porcentaje}% - {self.descripcion}"

    # --- ¡NUEVO! El pago se calcula a sí mismo ---
    def save(self, *args, **kwargs):
        # Si la cotización tiene un total, calculamos el valor
        if self.cotizacion and self.cotizacion.total:
            self.valor = (self.cotizacion.total * self.porcentaje) / 100
        super().save(*args, **kwargs)

class Cotizacion(models.Model):
    # --- CAMPOS DE RELACIÓN E IDENTIFICACIÓN (LOS QUE FALTABAN) ---
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    version = models.PositiveIntegerField(default=1)
    es_activa = models.BooleanField(default=True)
    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    valida_hasta = models.DateField()
    
    # --- CAMPOS DE TEXTO CON DEFAULTS ---
    TEXTO_CONDICIONES = """1. Forma de pago: 50% anticipo y 50% contra entrega.
2. La validez de la oferta es de 15 días.
3. Los precios incluyen IVA."""
    TEXTO_ENTREGA = "Tiempo de entrega: 3 a 5 días hábiles después de recibido el anticipo."
    TEXTO_GARANTIA = "Garantía de 1 año por defectos de fabricación e instalación."

    condiciones_comerciales = models.TextField(default=TEXTO_CONDICIONES, blank=True)
    tiempos_entrega = models.TextField(default=TEXTO_ENTREGA, blank=True)
    garantia = models.TextField(default=TEXTO_GARANTIA, blank=True)

    # --- CAMPOS DE TOTALES ---
    subtotal_antes_impuestos = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    porcentaje_impuestos = models.DecimalField(max_digits=5, decimal_places=2, default=19.00)
    valor_impuestos_calculado = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mostrar_impuestos_desglosados = models.BooleanField(default=False)

    # --- CAMPOS DE MONEDA ---
    MONEDA_CHOICES = [
        ('COP', 'Pesos Colombianos'),
        ('USD', 'Dólares Americanos'),
    ]
    moneda = models.CharField(max_length=3, choices=MONEDA_CHOICES, default='COP')
    trm = models.DecimalField("TRM (Tasa de cambio)", max_digits=10, decimal_places=2, default=1.0)

    def __str__(self):
        return f"Cotización V{self.version} para: {self.proyecto.nombre}"

    # --- LÓGICA DE CÁLCULO (MOTOR) ---
    def save(self, *args, **kwargs):
        # 1. Agrupar y sumar productos del proyecto
        resumen_productos = {}
        for detalle in self.proyecto.detalles.all():
            if detalle.producto:
                clave = detalle.producto.id
                descripcion = detalle.producto.nombre
                precio = detalle.precio_unitario_capturado
            else:
                clave = detalle.descripcion_manual
                descripcion = detalle.descripcion_manual
                precio = detalle.precio_unitario_capturado

            if clave not in resumen_productos:
                resumen_productos[clave] = {
                    'producto_obj': detalle.producto,
                    'descripcion': descripcion,
                    'cantidad_total': 0,
                    'precio_unitario': precio,
                    'garantia_meses': 0
                }
            
            resumen_productos[clave]['cantidad_total'] += detalle.cantidad
            
            if detalle.producto:
                garantia = detalle.garantia_especifica_meses or detalle.producto.garantia_default_meses
                resumen_productos[clave]['garantia_meses'] = garantia

        # 2. Calcular totales
        subtotal = sum(item['cantidad_total'] * item['precio_unitario'] for item in resumen_productos.values())
        
        # Conversión de moneda
        if self.moneda == 'USD' and self.trm > 1:
            subtotal = subtotal / self.trm

        impuestos = subtotal * (self.porcentaje_impuestos / 100)
        
        self.subtotal_antes_impuestos = subtotal
        self.valor_impuestos_calculado = impuestos
        self.total = subtotal + impuestos

        # Guardamos la cotización principal
        super().save(*args, **kwargs)

        # 3. ACTUALIZAR LOS PAGOS (Aquí se arregla el 0.00)
        # Como ya tenemos el self.total calculado arriba, ahora sí podemos calcular los porcentajes
        for pago in self.pagos.all():
            pago.valor = (self.total * pago.porcentaje) / 100
            pago.save()

        # 4. Recrear items
        self.items.all().delete()
        for clave, data in resumen_productos.items():
            precio_final = data['precio_unitario']
            if self.moneda == 'USD' and self.trm > 1:
                precio_final = precio_final / self.trm

            ItemCotizacion.objects.create(
                cotizacion=self,
                producto=data['producto_obj'],
                descripcion_agrupada=data['descripcion'],
                cantidad=data['cantidad_total'],
                precio_unitario=precio_final,
                garantia_meses=data.get('garantia_meses', 0)
            )

class ItemCotizacion(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)
    descripcion_agrupada = models.CharField(max_length=255)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    garantia_meses = models.PositiveIntegerField("Garantía (meses)", default=0)
    def subtotal(self): return self.cantidad * self.precio_unitario
    def __str__(self): return f"Resumen: {self.cantidad} x {self.descripcion_agrupada}"

# --- MÓDULO DE REMISIONES AUTOMATIZADAS DE ENTREGA ---
class Remision(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='remisiones')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    
    conductor = models.CharField(max_length=200, blank=True)
    placa_vehiculo = models.CharField(max_length=20, blank=True)
    empresa_transportadora = models.CharField(max_length=200, blank=True)
    
    recibido_por = models.CharField(max_length=200, blank=True)
    identificacion_receptor = models.CharField(max_length=50, blank=True)
    
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Remisión #{self.id} - {self.proyecto.nombre}"

    # --- LÓGICA DE AUTOMATIZACIÓN MEJORADA ---
    def save(self, *args, **kwargs):
        # Verificamos si es nueva
        es_nueva = self.pk is None
        
        super().save(*args, **kwargs)

        if es_nueva:
            # Copiamos TODOS los detalles del proyecto, uno por uno
            for detalle in self.proyecto.detalles.all():
                ItemRemision.objects.create(
                    remision=self,
                    producto=detalle.producto,
                    descripcion_variable=detalle.descripcion_manual,
                    cantidad=detalle.cantidad,
                    # --- ¡AQUÍ ESTÁ LA CLAVE! COPIAMOS LA UBICACIÓN ---
                    espacio=detalle.espacio,
                    sub_espacio=detalle.sub_espacio
                )

class ItemRemision(models.Model):
    remision = models.ForeignKey(Remision, related_name='items_remision', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion_variable = models.CharField(max_length=255, blank=True)
    
    # --- NUEVOS CAMPOS PARA GUARDAR LA UBICACIÓN ---
    espacio = models.CharField(max_length=200, blank=True)
    sub_espacio = models.CharField(max_length=200, blank=True)
    
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        nombre = self.producto.nombre if self.producto else self.descripcion_variable
        return f"{self.cantidad} - {nombre}"