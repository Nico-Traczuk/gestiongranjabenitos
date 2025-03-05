from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_http_methods 
from django.contrib.auth.decorators import login_required
from users.decorators import user_type_required
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.contrib import messages
from django.db import connection, DatabaseError
from .templates import *
from .models import *
import locale
from .forms import stockCompuestoForm, productosForm, gastosForm
from datetime import datetime, timedelta


@require_http_methods(["GET", "POST", "PUT", "DELETE"])
#-----------------------------------------------------------------------------

@login_required
@user_type_required(1)
def Viewhome(request):
    id_user = request.session.get('id_user')
    id_empresa = request.session.get('id_empresa')
    id_sucursal = request.session.get('id_sucursal')
    id_tipo_usuario = request.session.get('id_tipo_usuario')
    
    locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')
    date = datetime.now().date()
    print('\n ✅ Home')
    print('usuario: ', id_user)
    print('empresa: ', id_empresa)
    print('sucursal: ', id_sucursal)
    print('tipo de usuario: ', id_tipo_usuario)
    # Suma total general de las ventas
    totalVentas = ventas_cabecera.objects.aggregate(total_general=Sum('total_general'))['total_general'] or 0
    totalVentas_formateado = locale.format_string('%.2f', totalVentas, grouping=True)

    # Suma de kilos vendidos
    kilos_vendidos = ventas_detalle.objects.aggregate(total_kilos=Sum('cantidad'))['total_kilos'] or 0
    kilos = int(kilos_vendidos)
    gramos = int((kilos_vendidos - kilos) * 1000)
    kilos_vendidos_formateado = f"{kilos} kg {gramos} g"

    # 🔹 Agrupar ventas por fecha sumando el total del día
    ventas_por_fecha = (
        ventas_cabecera.objects
        .values('fecha_venta__date')  # Extraemos solo la fecha sin la hora
        .annotate(total=Sum('total_general'))  # Sumamos todas las ventas de ese día
        .order_by('fecha_venta__date')
    )

    fechas = [venta['fecha_venta__date'].strftime('%d-%m-%Y') for venta in ventas_por_fecha]
    ventas_totales = [venta['total'] for venta in ventas_por_fecha]

    return render(request, 'home.html', {
        'date': date,
        'totalVentas': totalVentas,
        'kilos_vendidos_formateado': kilos_vendidos_formateado,
        'totalVentas_formateado': totalVentas_formateado,
        'fechas': fechas,  # 🔹 Fechas agrupadas correctamente
        'ventas_totales': ventas_totales,  # 🔹 Total de ventas por fecha

    })
    

#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
@login_required
@user_type_required(1,2)
def Viewventas(request):
    search_query = request.GET.get('search', '')
    id_sucursal = request.session.get('id_sucursal')  # Obtener el id de la sucursal desde la sesión
    print('\n ✅ Ventas')
    print('estas en la sucursal: ', id_sucursal)
    if not id_sucursal:
        # Manejar el caso en el que no haya una sucursal en la sesión (redirigir o mostrar mensaje)
        return render(request, 'ventas.html', {'error': 'No se ha seleccionado una sucursal.'})

    # Filtrar productos por sucursal y búsqueda
    productos = articulo_sucursal.objects.filter(id_sucursal=id_sucursal)

    if search_query:
        productos = productos.filter(
            Q(id_articulo__descripcion__icontains=search_query) |
            Q(id_articulo__codigo_articulo__icontains=search_query)
        )

    return render(request, 'ventas.html', {
        'productos': productos,  # Pasar los productos filtrados al template
        'search_query': search_query,
    })
#-----------------------------------------------------------------------------
@login_required
@user_type_required(1)
def Viewreportes(request):
    ventas = venta_stock_compuesto.objects.all().order_by('-id_cabecera__fecha_venta')
    
    fecha_inicio = None
    fecha_fin = None

    if request.method == 'GET' and 'fecha_inicio' in request.GET and 'fecha_fin' in request.GET:
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')

        # Convertir a objetos datetime
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)  

        # Filtrar ventas por fecha
        ventas = ventas.filter(id_cabecera__fecha_venta__range=(fecha_inicio, fecha_fin))

    # Formatear el total de cada venta
    for venta in ventas:
        venta.id_detalle.total_formateado = "{:,.2f}".format(venta.id_detalle.total).replace(",", "X").replace(".", ",").replace("X", ".")

    # Paginación
    paginator = Paginator(ventas, 10)  # Muestra 10 ventas por página
    page_number = request.GET.get('page')  # Obtiene el número de página de la URL
    ventas_paginadas = paginator.get_page(page_number)

    return render(request, 'reportes.html', {
        'ventas_filtradas': ventas_paginadas,  # Se usa el objeto paginado
        'fecha_inicio': fecha_inicio.date() if fecha_inicio else None,
        'fecha_fin': fecha_fin.date() if fecha_fin else None
    })

#-----------------------------------------------------------------------------
@login_required
@user_type_required(1)

def ViewStockProducto(request):
#     """
#     BUSCA EN GOOGLE POR: python django how to join two table -REST
#     ENTRA A ESTA PAGINA: https://www.quora.com/How-do-I-join-tables-in-Django
#     """
    locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')
    
    # Formulario y consulta de productos
    producto_form = productosForm()

    # Obtener los productos de la base de datos
    id_empresa = request.session.get('id_empresa')
    sucursales_list = sucursales.objects.all()
    sucursal_seleccionada = request.GET.get('sucursal', '0')  # Valor por defecto '0'
    print(sucursal_seleccionada)

    if sucursal_seleccionada and sucursal_seleccionada != '0':
        print("✅ Se ha seleccionado una sucursal específica.")
        
        # Productos que ya están en la sucursal
        articulo_sucursal_objs = articulo_sucursal.objects.filter(id_sucursal_id=sucursal_seleccionada)
        
        # Ordenar por codigo_articulo (asegurando que sea numérico)
        productos_sucursal = articulo_sucursal_objs.order_by('id_articulo__codigo_articulo')
        
    else:
        print("✅ No se ha seleccionado una sucursal específica.")
        productos_sucursal = articulo_sucursal.objects.none()


    for producto in productos_sucursal:
    # Formateamos el precio con la configuración local de Argentina
        producto.precio_venta_formateado = locale.currency(producto.precio_venta, grouping=True)

    if request.method == 'POST':
        method = request.POST.get('_method')

        if method == 'UPDATE':  
            try:
                id_art = request.POST.get('id_articulo')
                articulo_obj = articulo_sucursal.objects.get(id_articulo=id_art)
                empresa_obj = articulo_empresa.objects.get(id_articulo=id_art)
                
                form = productosForm(request.POST, instance=articulo_obj)
                # Validación para asegurarse de que el código de artículo no se repita
                nuevo_codigo = request.POST.get('codigo_articulo')  # Código del form
                if nuevo_codigo and nuevo_codigo != empresa_obj.id_articulo.codigo_articulo:
                    # Actualizar código en la empresa (afecta a todas las sucursales)
                    empresa_obj.id_articulo.codigo_articulo = nuevo_codigo
                    empresa_obj.id_articulo.save()

                nuevo_precio = request.POST.get('precio_venta')
                if nuevo_precio:
                    articulo_obj.precio_venta = nuevo_precio
                    articulo_obj.save()
                # if form.is_valid():
                #     form.save()
                    print('codigo articulo: ', empresa_obj.id_articulo.codigo_articulo)
                    messages.success(request, "✅ Producto actualizado correctamente.")
                else:
                    messages.error(request, "❌ Error en la actualización del producto.")
            except articulos.DoesNotExist:
                messages.error(request, "❌ El producto no fue encontrado para actualizar.")

        elif method == 'DELETE':  
            try:
                id_articulo = request.POST.get('id_articulo')
                articulo_obj = articulos.objects.get(id_articulo=id_articulo)
                articulo_obj.delete()
                messages.success(request, "✅ Producto eliminado correctamente.")
            except articulos.DoesNotExist:
                messages.error(request, "❌ El producto no fue encontrado para eliminar.")

        else:  # Crear nuevo producto
            producto_form = productosForm(request.POST)

            # Validar si el código de artículo ya existe
            codigo_articulo = request.POST.get('codigo_articulo')  # Asumiendo que el campo es 'codigo_articulo'
            if articulos.objects.filter(codigo_articulo=codigo_articulo).exists():
                messages.error(request, "❌ El código de artículo ya está registrado. Por favor, use otro código.")
                return redirect('stockProducto')  # Redirigir para que el usuario pueda corregir el código
           
            # Si no hay código repetido, proceder con el guardado
            if producto_form.is_valid():
                empresa_obj = empresa.objects.get(id_empresa=id_empresa)  # Instancia de empresa
                nuevo_articulo = producto_form.save()
                print("✅ Producto creado correctamente.")
                print('producto de la empresa creado es: ', nuevo_articulo)
               
                id_articulo = nuevo_articulo.id_articulo
                articulo_obj = articulos.objects.get(id_articulo=id_articulo)  # Instancia del artículo

                if not id_empresa:
                    messages.error(request, "❌ No se encontró la empresa en la sesión.")
                    return redirect('stockProducto')

                # Crear la relación en articulo_empresa
                articulo_empresa.objects.create(
                    id_empresa=empresa_obj,  # Pasamos la instancia, no el ID
                    id_articulo=articulo_obj,  # Pasamos la instancia, no el ID
                    codigo_articulo=nuevo_articulo.codigo_articulo,  # Se mantiene el mismo código
                    precio_costo=nuevo_articulo.precio_costo,
                    precio_venta=nuevo_articulo.precio_venta
                )
                print("✅ Relación articulo_empresa creada correctamente.")   
                print("✅ Producto creado correctamente.")
                print('Producto de la empresa creado es:', nuevo_articulo)
                print('Datos enviados con POST:', request.POST)          
                messages.success(request, "✅ Producto creado correctamente.")
            else:
                messages.error(request, "❌ Error al crear el producto.")

        return redirect('stockProducto')

    # Contexto para la plantilla
    context = {
        # 'productos': productos_paginados,
        'producto_form': producto_form,
        'productos_sucursal': productos_sucursal,
        'sucursales': sucursales_list,
        'sucursal_seleccionada': sucursal_seleccionada
    }

    return render(request, 'stockProductos.html', context)
#-----------------------------------------------------------------------------
@login_required
@user_type_required(1)
def ViewArticulosSucursal(request):
    sucursales_list = sucursales.objects.all()
    sucursal_seleccionada = request.GET.get('sucursal', '0')

    print(f"\n🔹 Sucursal seleccionada: {sucursal_seleccionada}")

    productos = []
    empresa_list = articulo_empresa.objects.all()  # Mostrar todos los artículos por defecto

    if sucursal_seleccionada and sucursal_seleccionada != '0':
        print("✅ Se ha seleccionado una sucursal específica.")

        # Obtener los productos ya en la sucursal
        articulo_sucursal_objs = articulo_sucursal.objects.filter(id_sucursal_id=sucursal_seleccionada)
        productos = sorted(
            [obj.id_articulo for obj in articulo_sucursal_objs], 
            key=lambda articulo: int(articulo.codigo_articulo)
        )

        # Obtener los artículos que NO están en la sucursal
        articulos_asignados_ids = articulo_sucursal_objs.values_list('id_articulo', flat=True)
        empresa_list = articulo_empresa.objects.exclude(id_articulo__in=articulos_asignados_ids)

    # **IMPORTANTE:** Si `productos` está vacío, aseguramos que sea una lista vacía
    if not productos:
        productos = []

    # **IMPORTANTE:** Si `empresa_list` está vacío, aseguramos que sea una lista vacía
    if not empresa_list:
        empresa_list = []

    print(f"🔹 Productos en la sucursal ({sucursal_seleccionada}): {[p.descripcion for p in productos]}")
    print(f"🔹 Artículos disponibles para agregar: {[e.id_articulo.descripcion for e in empresa_list]}")

    context = {
        'sucursales': sucursales_list,
        'productos': productos,  # Siempre se enviará la lista, aunque esté vacía
        'sucursal_seleccionada': sucursal_seleccionada,
        'empresa_list': empresa_list  # Siempre se enviará la lista, aunque esté vacía
    }

    return render(request, 'articulosSucursal.html', context)

#-----------------------------------------------------------------------------
@login_required
def agregar_articulo(request):
    if request.method == "POST":
        id_sucursal = request.POST.get("sucursal_id", "").strip()
        articulos_a_agregar = request.POST.getlist("articulos_a_agregar")

        print("ID Sucursal:", id_sucursal)
        print("Artículos a agregar antes de limpiar:", articulos_a_agregar)

        # Filtramos valores vacíos
        articulos_a_agregar = [id for id in articulos_a_agregar if id.strip()]

        print("Artículos a agregar después de limpiar:", articulos_a_agregar)

        if id_sucursal and id_sucursal.isdigit() and articulos_a_agregar:
            try:
                sucursal = sucursales.objects.get(id_sucursal=id_sucursal)
            except sucursales.DoesNotExist:
                print("Error: La sucursal no existe.")
                return redirect(f"/articulosSucursal?sucursal={id_sucursal}")

            for id_articulo in articulos_a_agregar:
                try:
                    # Obtener el artículo desde `articulo_empresa`
                    articulo_empresa_obj = articulo_empresa.objects.get(id_articulo=id_articulo)
                    articulo = articulo_empresa_obj.id_articulo  # Extraer el objeto artículo real

                    # Verificar si ya existe en la sucursal para evitar duplicados
                    if not articulo_sucursal.objects.filter(id_articulo=articulo, id_sucursal=sucursal).exists():
                        articulo_sucursal.objects.create(id_articulo=articulo, id_sucursal=sucursal)
                except articulo_empresa.DoesNotExist:
                    print(f"Error: El artículo con ID {id_articulo} no existe en articulo_empresa.")

        return redirect(f"/articulosSucursal?sucursal={id_sucursal}")

#-----------------------------------------------------------------------------
@login_required
def quitar_articulo(request):
    if request.method == "POST":
        id_sucursal = request.POST.get("sucursal_id", "").strip()
        articulos_a_quitar = request.POST.getlist("articulos_a_quitar")

        print("ID Sucursal:", id_sucursal)
        print("Artículos a quitar antes de limpiar:", articulos_a_quitar)

        # Filtramos valores vacíos
        articulos_a_quitar = [id for id in articulos_a_quitar if id.strip()]

        print("Artículos a quitar después de limpiar:", articulos_a_quitar)

        if id_sucursal and id_sucursal.isdigit() and articulos_a_quitar:
            try:
                sucursal = sucursales.objects.get(id_sucursal=id_sucursal)
            except sucursales.DoesNotExist:
                print("Error: La sucursal no existe.")
                return redirect(f"/articulosSucursal?sucursal={id_sucursal}")

            # Eliminamos los artículos de la sucursal usando id_articulo
            articulo_sucursal.objects.filter(
                id_articulo__id_articulo__in=[int(id) for id in articulos_a_quitar],  
                id_sucursal=sucursal
            ).delete()

        return redirect(f"/articulosSucursal?sucursal={id_sucursal}")
#-----------------------------------------------------------------------------
def get_producto_data(request, id_articulo):
    try:
        articulo = articulos.objects.get(id_articulo=id_articulo)
        data = {
            'id_articulo': articulo.id_articulo,
            'id_unidad': articulo.id_unidad.id_unidad if articulo.id_unidad else None,
            'id_categoria': articulo.id_categoria.id_categoria if articulo.id_categoria else None,
            'codigo_articulo': articulo.codigo_articulo,
            'descripcion': articulo.descripcion,
            'precio_venta': articulo.precio_venta,  
        }
        return JsonResponse(data)
    except articulos.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


#-----------------------------------------------------------------------------

@login_required
@user_type_required(1)
def ViewStockCompuesto(request):
    # Obtener datos de la sesión
    id_sucursal = request.session.get('id_sucursal')
    id_empresa = request.session.get('id_empresa')
    id_usuario = request.session.get('id_usuario')
    id_tipo_usuario = request.session.get('id_tipo_usuario')

    # Formulario y consulta de productos compuestos
    compuesto_form = stockCompuestoForm()
    productosCompuestos = stock_compuesto.objects.all()

    # Obtener el peso vendido por cada stock compuesto
    stock_vendido = venta_stock_compuesto.objects.values('id_stock_compuesto').annotate(
        peso_vendido=Sum('peso')
    )

    # Convertirlo en un diccionario {id_stock_compuesto: peso_vendido}
    stock_vendido_dict = {item['id_stock_compuesto']: item['peso_vendido'] or 0 for item in stock_vendido}

    # Agregar peso vendido a cada producto compuesto
    for producto in productosCompuestos:
        producto.peso_vendido = stock_vendido_dict.get(producto.id_stock_compuesto, 0)

    if request.method == 'POST':
        method = request.POST.get('_method')

        if method == 'UPDATE':
            try:
                id_stock_comp = request.POST.get('id_stock_compuesto')
                stock_compuesto_obj = stock_compuesto.objects.get(id_stock_compuesto=id_stock_comp)
                form = stockCompuestoForm(request.POST, instance=stock_compuesto_obj)
                if form.is_valid():
                    form.save()
                    messages.success(request, "✅ Producto compuesto actualizado correctamente.")
                else:
                    messages.error(request, "❌ Error al actualizar el producto compuesto.")
            except stock_compuesto.DoesNotExist:
                messages.error(request, "❌ El producto compuesto no fue encontrado para actualizar.")

        elif method == 'DELETE':
            try:
                id_stock_compuesto = request.POST.get('id_stock_compuesto')
                stock_compuesto_obj = stock_compuesto.objects.get(id_stock_compuesto=id_stock_compuesto)
                stock_compuesto_obj.delete()
                messages.success(request, "✅ Producto compuesto eliminado correctamente.")
            except stock_compuesto.DoesNotExist:
                messages.error(request, "❌ El producto compuesto no fue encontrado para eliminar.")

        else:
            compuesto_form = stockCompuestoForm(request.POST)
            if compuesto_form.is_valid():
                compuesto_form.save()
                messages.success(request, "✅ Producto compuesto creado correctamente.")
            else:
                messages.error(request, "❌ Error al crear el producto compuesto.")

        return redirect('stockCompuesto')

    # Contexto para la plantilla
    context = {
        'productosCompuestos': productosCompuestos,
        'compuesto_form': compuesto_form,
        'id_sucursal': id_sucursal,
        'id_empresa': id_empresa,
        'id_usuario': id_usuario,
        'id_tipo_usuario': id_tipo_usuario,
    }
    return render(request, 'stockCompuestos.html', context)
#-----------------------------------------------------------------------------

def viewProductoRelacionados(request):
    return render(request, 'productosRelacionados.html')

#-----------------------------------------------------------------------------
@login_required
@user_type_required(1)
def ViewCostos(request):
    if request.method == "POST":
        costos_form = gastosForm(request.POST)  # Recibir datos del formulario
        if costos_form.is_valid():
            costos_form.save()  # Guardar en la base de datos
            return redirect("costos")  # Redirigir para limpiar el formulario

    else:
        costos_form = gastosForm()  # Mostrar formulario vacío en una petición GET

    context = {
        "costos_form": costos_form
    }
    return render(request, "costos.html", context)

#-----------------------------------------------------------------------------

@login_required
@user_type_required(1)
def ViewCostosTabla(request):
    costos_list = gastos.objects.all()  # Obtener todos los costos

    # Formatear los montos
    for costo in costos_list:
        costo.monto_formateado = "{:,.2f}".format(costo.monto).replace(",", "X").replace(".", ",").replace("X", ".")

    # Configurar la paginación (10 registros por página)
    paginator = Paginator(costos_list, 10)  
    page_number = request.GET.get("page")  # Obtener el número de página de la URL
    costos = paginator.get_page(page_number)  # Obtener los datos de la página actual

    context = {
        "costos": costos
    }
    return render(request, "costosTabla.html", context)

#-----------------------------------------------------------------------------


# Vista para procesar la venta
@login_required
@user_type_required(1,2)
def procesar_venta(request):
    if request.method != 'POST':
        messages.error(request, 'Método no permitido')
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    try:
        print("\n🔹 RECIBIENDO SOLICITUD DE VENTA 🔹")

        id_medio_pago = request.POST.get('id_medio_pago')
        total = request.POST.get('total')

        if not id_medio_pago or not total:
            messages.error(request, 'Faltan datos de la cabecera')
            return JsonResponse({'status': 'error', 'message': 'Faltan datos de la cabecera'}, status=400)

        # Crear cabecera de la venta
        cabecera = ventas_cabecera.objects.create(
            id_empresa_id=request.session.get('id_empresa'),
            id_sucursal_id=request.session.get('id_sucursal'),
            id_medio_pago_id=int(id_medio_pago),
            fecha_venta=datetime.now(),
            total_general=float(total)
        )

        id_cabecera = cabecera.id_cabecera
        print(f"✅ Cabecera creada con ID: {id_cabecera} en la surucsal {request.session.get('id_sucursal')}")


        detalles = []
        ids_articulos = request.POST.getlist("detalles_id_articulo[]")
        cantidades = request.POST.getlist("detalles_cantidad[]")
        precios_unitarios = request.POST.getlist("detalles_precio_unitario[]")
        totales = request.POST.getlist("detalles_total[]")

        if not (ids_articulos and cantidades and precios_unitarios and totales):
            messages.error(request, 'Datos de detalle incompletos')
            return JsonResponse({'status': 'error', 'message': 'Datos de detalle incompletos'}, status=400)

        # Obtener el id_sucursal desde la sesión
        id_sucursal = request.session.get('id_sucursal')

        # Filtramos los artículos de la sucursal
        articulo_sucursal_objs = articulo_sucursal.objects.filter(id_sucursal_id=id_sucursal)

        # Procesamos los detalles
        for i in range(len(ids_articulos)):
            id_articulo = int(ids_articulos[i])

            # Verificamos si el artículo pertenece a la sucursal
            articulo_sucursal_obj = articulo_sucursal_objs.filter(id_articulo_id=id_articulo).first()

            if not articulo_sucursal_obj:
                messages.error(request, f"El artículo con ID {id_articulo} no pertenece a la sucursal seleccionada")
                return JsonResponse({'status': 'error', 'message': f"El artículo con ID {id_articulo} no pertenece a la sucursal seleccionada"}, status=400)

            detalle = {
                "id_articulo": id_articulo,
                "cantidad": float(cantidades[i]),
                "precio_unitario": float(precios_unitarios[i]),
                "total": float(totales[i])
            }
            detalles.append(detalle)

        # Guardar los detalles en la base de datos
        for detalle in detalles:
            ventas_detalle.objects.create(
                id_cabecera=cabecera,
                id_articulo_id=detalle["id_articulo"],
                cantidad=detalle["cantidad"],
                precio_unitario=detalle["precio_unitario"],
                total=detalle["total"]
            )

        print(f"✅ Venta con ID {id_cabecera} procesada correctamente.")

        # 🔹 **Ejecución del Stored Procedure**
        try:
            cursor = connection.cursor()
            cursor.execute("EXEC sp_actualiza_stock %s", [id_cabecera])
            cursor.close()
            print(f"✅ SP ejecutado con ID: {id_cabecera}")

        except DatabaseError as ex:
            messages.error(request, f'Error al actualizar stock: {str(ex)}')
            return JsonResponse({'status': 'error', 'message': f'Error al actualizar stock: {str(ex)}'}, status=500)

        messages.success(request, 'Venta procesada correctamente')
        return redirect('ventas')

    except Exception as e:
        messages.error(request, f'Error interno: {str(e)}')
        return JsonResponse({'status': 'error', 'message': f'Error interno: {str(e)}'}, status=500)

#-----------------------------------------------------------------------------------------
@login_required
@user_type_required(1)
def ViewReporteCompuesto(request):
    id_empresa = 1

    if not id_empresa:
        return JsonResponse({'status': 'error', 'message': 'No se encontró una empresa en la sesión'}, status=400)

    try:
        # Ejecutar la consulta a la vista SQL
        cursor = connection.cursor()
        cursor.execute("""
            SELECT * FROM v_movimientos_stock_compuesto 
            WHERE id_empresa = %s
        """, [id_empresa])

        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()

    except DatabaseError as ex:
        print(f"❌ Error al ejecutar la consulta: {ex}")
        return JsonResponse({'status': 'error', 'message': f'Error al obtener los datos: {str(ex)}'}, status=500)

    # Paginación
    page = request.GET.get('page', 1)  # Obtener el número de página de la URL
    paginator = Paginator(results, 10)  # 10 registros por página

    try:
        movimientos_paginados = paginator.page(page)
    except:
        movimientos_paginados = paginator.page(1)  # Si hay error, carga la primera página

    return render(request, 'reporteStockCompuesto.html', {
        'movimientos': movimientos_paginados
    })







        # ?? **query a la vista**
        # try:
        #     #Podes agregar mas condiciones al WHERE segun los filtros
        #     cursor = connection.cursor()
        #     cursor.execute("SELECT * FROM v_movimientos_stock_compuesto \
        #                    WHERE id_empresa = %s ", [request.session['id_empresa']])  
        #     result = cursor.fetchall()
        #     cursor.close()            

        # except DatabaseError as ex:
        #     print(f"? Error al ejecutar VISTA: {ex}")
        #     return JsonResponse({'status': 'error', 'message': f'Error al actualizar stock: {str(ex)}'}, status=500)
