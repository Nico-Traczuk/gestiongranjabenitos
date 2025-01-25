from django.db import models

# Create your models here.

        
class empresa (models.Model):
    id_empresa = models.AutoField(primary_key=True, db_column='id_empresa')
    nombre_empresa = models.CharField(max_length=50)
    cuit_empresa = models.CharField(max_length=13, unique=True)
    direccion = models.TextField(max_length=100)
    telefono = models.CharField(max_length=40)
    email = models.EmailField(max_length=50)
    class Meta:
        db_table = "empresa"
        
class sucursales (models.Model):
    id_sucursal = models.AutoField(primary_key=True)
    id_empresa = models.ForeignKey(empresa, on_delete=models.CASCADE, db_column='id_empresa', default='1')
    nombre_sucursal = models.CharField(max_length=50)
    direccion = models.TextField(max_length=100)
    telefono = models.IntegerField()
    email = models.EmailField(max_length=50)
    
    class Meta:
        db_table = "sucursales"

class categorias (models.Model):
    id_categoria = models.AutoField(primary_key=True)
    categoria = models.CharField(max_length=50)
    def __str__(self):
        return self.categoria
    class Meta:
        db_table = "categorias"

        
class tipo_unidad (models.Model):
    id_unidad = models.AutoField(primary_key=True)
    tipo_unidad = models.CharField(max_length=50)
    def __str__(self):
        return self.tipo_unidad
    class Meta:
        db_table = "tipo_unidad"        
    
class articulo_compuesto (models.Model):
    id_compuesto = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)
    id_categoria = models.ForeignKey(categorias, on_delete=models.CASCADE, db_column='id_categoria', default='1')
    id_unidad = models.ForeignKey(tipo_unidad, on_delete=models.CASCADE, db_column='id_unidad', default='1')
    def __str__(self):
        return self.descripcion
    class Meta:
        db_table = "articulo_compuesto"

class articulos (models.Model):
    id_articulo = models.AutoField(primary_key=True)
    id_empresa = models.ForeignKey(empresa, on_delete=models.CASCADE, db_column='id_empresa', default='1')
    id_unidad = models.ForeignKey(tipo_unidad, on_delete=models.CASCADE, db_column='id_unidad', default='1')
    id_categoria = models.ForeignKey(categorias, on_delete=models.CASCADE, db_column='id_categoria', default='1')
    codigo_articulo = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)
    peso_promedio = models.DecimalField(max_digits=25, decimal_places=3, default='0')
    variacion= models.DecimalField(max_digits=25, decimal_places=3, default='0')
    precio_costo = models.DecimalField(max_digits=25, decimal_places=3, default='0')
    precio_venta = models.DecimalField(max_digits=25, decimal_places=3, default='0')
    class Meta:
        db_table = "articulos"


class articulo_composicion (models.Model):
    id_composicion = models.AutoField(primary_key=True)
    id_compuesto = models.ForeignKey(articulo_compuesto, on_delete=models.CASCADE, db_column='id_compuesto', default='1')
    id_articulo = models.ForeignKey(articulos, on_delete=models.CASCADE, db_column='id_articulo', default='1')
    proporcion = models.DecimalField(max_digits=25, decimal_places=3, default='0')
    class Meta:
        db_table = "articulo_composicion"


class articulo_sucursal (models.Model):
    id_articulo = models.ForeignKey(articulos, on_delete=models.CASCADE, db_column='id_articulo', default='1')
    id_sucursal = models.ForeignKey(sucursales, on_delete=models.CASCADE, db_column='id_sucursal', default='1')
    class Meta:
        db_table = "articulo_sucursal"

class stock_compuesto (models.Model):
    id_stock_compuesto = models.AutoField(primary_key=True)
    id_compuesto = models.ForeignKey(articulo_compuesto, on_delete=models.CASCADE, db_column='id_compuesto', default='1')
    cantidad_ingresada = models.DecimalField(max_digits=25, decimal_places=3, default='0')
    peso_inicial = models.DecimalField(max_digits=25, decimal_places=3, default='0')
    peso_venta = models.DecimalField(max_digits=25, decimal_places=3, default='0')
    fecha_actualizacion = models.DateTimeField(blank=True , null=True)
    def __str__(self):
        return self.id_compuesto
    class Meta:
        db_table = "stock_compuesto" 

class stock (models.Model):
    id_stock = models.AutoField(primary_key=True)
    id_articulo = models.ForeignKey(articulos, on_delete=models.CASCADE, db_column='id_articulo', default='1') 
    fecha_actualizacion = models.DateTimeField(blank=True , null=True)
    class Meta:
        db_table = "stock"
        
class medio_pago (models.Model):
    id_medio_pago = models.AutoField(primary_key=True, db_column='id_medio_pago')
    medio_pago = models.CharField(max_length=50)
    class Meta:
        db_table = "medio_pago"
 
class ventas_cabecera (models.Model):
    id_cabecera = models.AutoField(primary_key=True)
    id_empresa = models.ForeignKey(empresa, on_delete=models.CASCADE, db_column='id_empresa')
    id_sucursal = models.ForeignKey(sucursales, on_delete=models.CASCADE, db_column='id_sucursal')
    id_medio_pago = models.ForeignKey(medio_pago, on_delete=models.CASCADE, db_column='id_medio_pago')
    id_categoria = models.ForeignKey(categorias, on_delete=models.CASCADE, db_column='id_categoria', default='1')
    fecha_venta = models.DateTimeField()
    total_general = models.FloatField()
    class Meta:
        db_table = "ventas_cabecera"

class ventas_detalle (models.Model):
    id_detalle = models.AutoField(primary_key=True)
    id_cabecera = models.ForeignKey(ventas_cabecera, on_delete=models.CASCADE, db_column='id_cabecera')
    id_articulo = models.ForeignKey(articulos, on_delete=models.CASCADE, db_column='id_articulo', default='1')
    cantidad = models.DecimalField(max_digits=25, decimal_places=3)
    precio_unitario = models.DecimalField(max_digits=25, decimal_places=3)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        db_table = "ventas_detalle"


# class lista_precios (models.Model):
#     id_lista_precios = models.AutoField(primary_key=True)
#     fecha_lista = models.DateTimeField()
#     vigente = models.BooleanField()
#     class Meta:
#         db_table = "lista_precios"
        
# class lista_precios_detalle (models.Model):
#     id_lista_detalle = models.AutoField(primary_key=True)
#     id_lista_precios = models.ForeignKey(lista_precios, on_delete=models.CASCADE, db_column='id_lista_precios')
#     id_articulo = models.ForeignKey(articulos, on_delete=models.CASCADE, db_column='id_articulo', default='1')
#     precio_costo = models.DecimalField(max_digits=25, decimal_places=3)
#     precio_venta = models.DecimalField(max_digits=25, decimal_places=3)
#     class Meta:
#         db_table = "lista_precios_detalle"