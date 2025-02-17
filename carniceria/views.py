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
    locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')
    date = datetime.now().date()

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
        'ventas_totales': ventas_totales  # 🔹 Total de ventas por fecha
    })

#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
@login_required
@user_type_required(1,2)
def Viewventas(request):
    search_query = request.GET.get('search', '')
    
    # Filter products based on search query with correct field names
    if search_query:
        productos = articulos.objects.filter(
            Q(descripcion__icontains=search_query) |
            Q(codigo_articulo__icontains=search_query)  # Changed from codigo to codigo_articulo
        )
    else:
        productos = articulos.objects.all()
    
    return render(request, 'ventas.html', {
        'productos': productos,
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
    # Obtener datos de la sesión
    id_sucursal = request.session.get('id_sucursal')
    id_empresa = request.session.get('id_empresa')
    id_usuario = request.session.get('id_usuario')
    id_tipo_usuario = request.session.get('id_tipo_usuario')

    # Formulario y consulta de productos
    producto_form = productosForm()
    productos = articulos.objects.all()  

    if request.method == 'POST':
        method = request.POST.get('_method')

        if method == 'UPDATE':  
            try:
                id_art = request.POST.get('id_articulo')
                articulo_obj = articulos.objects.get(id_articulo=id_art)
                form = productosForm(request.POST, instance=articulo_obj)

                # Validación para asegurarse de que el código de artículo no se repita
                codigo_articulo = request.POST.get('codigo_articulo')  # Obtener el código de artículo
                if articulos.objects.filter(codigo_articulo=codigo_articulo).exclude(id_articulo=id_art).exists():
                    messages.error(request, "❌ El código de artículo ya está registrado. Por favor, use otro código.")
                    return redirect('stockProducto')  # Redirigir para corregir el código

                if form.is_valid():
                    form.save()
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
                producto_form.save()
                messages.success(request, "✅ Producto creado correctamente.")
            else:
                messages.error(request, "❌ Error al crear el producto.")

        return redirect('stockProducto')

    # Paginación
    paginator = Paginator(productos, 10)
    page = request.GET.get('page')

    try:
        productos_paginados = paginator.page(page)
    except PageNotAnInteger:
        productos_paginados = paginator.page(1)
    except EmptyPage:
        productos_paginados = paginator.page(paginator.num_pages)

    # Contexto para la plantilla
    context = {
        'productos': productos_paginados,
        'producto_form': producto_form,
        'id_sucursal': id_sucursal,
        'id_empresa': id_empresa,
        'id_usuario': id_usuario,
        'id_tipo_usuario': id_tipo_usuario,
    }

    return render(request, 'stockProductos.html', context)
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
            id_empresa_id=1,
            id_sucursal_id=1,
            id_medio_pago_id=int(id_medio_pago),
            fecha_venta=datetime.now(),
            total_general=float(total)
        )

        id_cabecera = cabecera.id_cabecera
        print(f"✅ Cabecera creada con ID: {id_cabecera}")

        detalles = []
        ids_articulos = request.POST.getlist("detalles_id_articulo[]")
        cantidades = request.POST.getlist("detalles_cantidad[]")
        precios_unitarios = request.POST.getlist("detalles_precio_unitario[]")
        totales = request.POST.getlist("detalles_total[]")

        if not (ids_articulos and cantidades and precios_unitarios and totales):
            messages.error(request, 'Datos de detalle incompletos')
            return JsonResponse({'status': 'error', 'message': 'Datos de detalle incompletos'}, status=400)

        for i in range(len(ids_articulos)):
            detalle = {
                "id_articulo": int(ids_articulos[i]),
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
