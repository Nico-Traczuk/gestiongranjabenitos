from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_http_methods 
from django.contrib.auth.decorators import login_required
from users.decorators import user_type_required
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.db import connection, DatabaseError
from .templates import *
from .models import *
from .forms import stockCompuestoForm, productosForm, gastosForm
from datetime import datetime, timedelta


@require_http_methods(["GET", "POST", "PUT", "DELETE"])
#-----------------------------------------------------------------------------

@login_required
@user_type_required(1)
def Viewhome(request):
    #HARDCODE LAS VARIABLES DE SESION (ID SUC, ID EMPRESA, ID USUARIO, ID TIPO USUARIO) ESTO SE LLENA EN EL LOGIN
    # request.session['id_sucursal'] = 1
    # request.session['id_empresa'] = 1
    # request.session['id_usuario'] = 1
    # request.session['id_tipo_usuario'] = 1

    date = datetime.now().date
    totalVentas = ventas_cabecera.objects.aggregate(total_general=Sum('total_general'))['total_general']
    kilos_vendidos = ventas_detalle.objects.aggregate(total_kilos=Sum('cantidad'))['total_kilos']
    kilos = int(kilos_vendidos)
    gramos = int((kilos_vendidos - kilos) * 1000)
    kilos_vendidos_formateado = f"{kilos} kg {gramos} g"
    return render(request, 'home.html', {'date': date,  'totalVentas': totalVentas, 'kilos_vendidos_formateado': kilos_vendidos_formateado})


#-----------------------------------------------------------------------------
"""    

	MODALES

		NUEVO: agregar JS en el boton que modifique el METHOD a POST
		BORRAR: agregar JS en el boton que modifique el METHOD a DELETE
		MODIFICAR: agregar JS en el boton que modifique el METHOD a PUT

		Haciendo eso, el boton OK del modal siemrpe actuar� como SUBMIT

	NUEVO:
		tomas el ID del compuesto (en el caso que lo haya definido) ESTE TE DEFINE SI VA A PERTENECER A UN COMPUESTO O NO
		tomas todos los datos del articulo
		validas
		grabas el articulo
		pedis el ID nuevo generado (objeto_art.id)

		si el articulo tiene definido el ID de compuesto
			tomas los datos para crear un registro en el modelo art_composicion
			grabas

		Si el tipo es admin
			recorres todas las sucrusales de la empresa
			y por cada sucursal
			agregas el nuevo articulo
		Si el tipo es operador y puede agregar articulos
			tomas la sucursal del tipo
			y agrega el articulo para esa sucursal 
	"""

#            producto_id = request.PUT.get('id_articulo')
#            try:
#                producto = articulos.objects.get(id_articulo=int(producto_id))
#                form = productosForm(instance=producto)
#                return redirect('stock')
#            except articulos.DoesNotExist:
#                return redirect('stock')


	


"""
		elif 'agregar_producto_padre' in request.POST:
			form_padre = stockCompuestoForm(request.POST)
			if form_padre.is_valid():
				form_padre.save()
				return redirect('stock')
		elif 'eliminar_producto' in request.POST:
			producto_id = request.POST.get('id_articulo')
			try:
				producto = articulos.objects.get(id_articulo=int(producto_id))
				producto.delete()
				return redirect('stock')
			except articulos.DoesNotExist:
				return redirect('stock')
		elif 'eliminar_stock_compuesto' in request.POST:
			stock_compuesto_id = request.POST.get('eliminar_stock_compuesto')
			try:
				stock_compuesto_obj = stock_compuesto.objects.get(id_stock_compuesto=stock_compuesto_id)
				stock_compuesto_obj.delete()
				return redirect('stock')
			except stock_compuesto.DoesNotExist:
				return redirect('stock')
		elif 'modificar_producto' in request.PUT:
			print('modificar_producto', request.PUT)
			producto_id = request.PUT.get('id_articulo')
			try:
				producto = articulos.objects.get(id_articulo=int(producto_id))
				form = productosForm(instance=producto)
				return redirect('stock')
			except articulos.DoesNotExist:
				return redirect('stock')
		elif 'modificar_stock_compuesto' in request.PUT:
			print('modificar_stock_compuesto', request.PUT)
			stock_compuesto_id = request.PUT.get('modificar_stock_compuesto')
			try:
				stock_compuesto_obj = stock_compuesto.objects.get(id_stock_compuesto=int(stock_compuesto_id) )
				form_padre = stockCompuestoForm(instance=stock_compuesto_obj)
				return redirect('stock')
			except stock_compuesto.DoesNotExist:
				return redirect('stock')
	"""
#            producto_id = request.POST.get('id_articulo')
#            try:
#                producto = articulos.objects.get(id_articulo=int(producto_id))
#                producto.delete()
#                return redirect('stock')
#            except articulos.DoesNotExist:
#                return redirect('stock')

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
    productos = articulos.objects.all()  # Filtrar por empresa y sucursal si es necesario

    if request.method == 'POST':
        method = request.POST.get('_method')  # Para manejar PUT y DELETE desde formularios HTML

        if method == 'UPDATE':  # Actualizar un producto existente
            try:
                id_art = request.POST.get('id_articulo')
                print(id_art, 'id del articulo')
                articulo_obj = articulos.objects.get(id_articulo=id_art)
                form = productosForm(request.POST, instance=articulo_obj)
                if form.is_valid():
                    form.save()
                    print("Producto actualizado correctamente.")
                else:
                    print("Error en el formulario de actualización.", form.errors)
            except articulos.DoesNotExist:
                print("Error: El producto no fue encontrado (UPDATE).")

        elif method == 'DELETE':  # Eliminar un producto existente
            try:
                id_articulo = request.POST.get('id_articulo')
                articulo_obj = articulos.objects.get(id_articulo=id_articulo)
                articulo_obj.delete()
                print("Producto eliminado correctamente.")
            except articulos.DoesNotExist:
                print("Error: El producto no fue encontrado (DELETE).")

        else:  # Crear un nuevo producto
            producto_form = productosForm(request.POST)
            if producto_form.is_valid():
                producto_form.save()
                print("Producto creado correctamente.")
            else:
                print("Error en el formulario de creación.", producto_form.errors)

        # Redirigir a la misma vista para evitar reenvíos del formulario
        return redirect('stockProducto')

    # Paginación de productos
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

    if request.method == 'POST':
        method = request.POST.get('_method')
        print(f"Método recibido: {method}")  # Depuración: Verificar el método (CREATE, UPDATE, DELETE)

        if method == 'UPDATE':
            try:
                id_stock_comp = request.POST.get('id_stock_compuesto')
                print(f"ID de stock compuesto para actualizar: {id_stock_comp}")  # Depuración: Verificar el ID
                stock_compuesto_obj = stock_compuesto.objects.get(id_stock_compuesto=id_stock_comp)
                form = stockCompuestoForm(request.POST, instance=stock_compuesto_obj)
                if form.is_valid():
                    form.save()
                    print("Producto compuesto actualizado correctamente.")  # Depuración: Confirmar actualización
                else:
                    print("Error en el formulario de actualización.")  # Depuración: Formulario no válido
            except stock_compuesto.DoesNotExist:
                print("Error: El registro no fue encontrado (UPDATE).")  # Depuración: Registro no existe

        elif method == 'DELETE':
            try:
                id_stock_compuesto = request.POST.get('id_stock_compuesto')
                print(f"ID de stock compuesto para eliminar: {id_stock_compuesto}")  # Depuración: Verificar el ID
                stock_compuesto_obj = stock_compuesto.objects.get(id_stock_compuesto=id_stock_compuesto)
                stock_compuesto_obj.delete()
                print("Producto compuesto eliminado correctamente.")  # Depuración: Confirmar eliminación
            except stock_compuesto.DoesNotExist:
                print("Error: El registro no fue encontrado (DELETE).")  # Depuración: Registro no existe

        else:
            compuesto_form = stockCompuestoForm(request.POST)
            if compuesto_form.is_valid():
                compuesto_form.save()
                print("Producto compuesto creado correctamente.")  # Depuración: Confirmar creación
            else:
                print("Error en el formulario de creación.", compuesto_form.errors)  # Depuración: Formulario no válido
		        
        # Redirigir a la misma vista para evitar reenvíos del formulario
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
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    try:
        print("\n🔹 RECIBIENDO SOLICITUD DE VENTA 🔹")
        print(f"🔍 Datos crudos recibidos en request.POST: {request.POST}")

        # Extraer datos de la cabecera
        id_medio_pago = request.POST.get('id_medio_pago')
        total = request.POST.get('total')

        if not id_medio_pago or not total:
            print("❌ Error: Datos incompletos en la cabecera de la venta")
            return JsonResponse({'status': 'error', 'message': 'Faltan datos de la cabecera'}, status=400)

        # Crear cabecera de la venta
        cabecera = ventas_cabecera.objects.create(
            id_empresa_id = 1,  # Ajustar según el usuario logueado
            id_sucursal_id = request.session['id_sucursal'],  # Ajustar según la sucursal del usuario
            id_medio_pago_id = int(id_medio_pago),
            fecha_venta = datetime.now(),
            total_general = float(total)
        )

        id_cabecera = cabecera.id_cabecera  # Obtener el ID recién creado
        print(f"✅ Cabecera creada con ID: {id_cabecera}")

        # Procesar los detalles de la venta
        detalles = []
        ids_articulos = request.POST.getlist("detalles_id_articulo[]")
        cantidades = request.POST.getlist("detalles_cantidad[]")
        precios_unitarios = request.POST.getlist("detalles_precio_unitario[]")
        totales = request.POST.getlist("detalles_total[]")

        if not (ids_articulos and cantidades and precios_unitarios and totales):
            print("❌ Error: Datos incompletos en los detalles de la venta")
            return JsonResponse({'status': 'error', 'message': 'Datos de detalle incompletos'}, status=400)

        for i in range(len(ids_articulos)):
            detalle = {
                "id_articulo": int(ids_articulos[i]),
                "cantidad": float(cantidades[i]),
                "precio_unitario": float(precios_unitarios[i]),
                "total": float(totales[i])
            }
            detalles.append(detalle)
            print(f"🛒 Detalle {i+1}: {detalle}")

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
            print(f"❌ Error al ejecutar SP: {ex}")
            return JsonResponse({'status': 'error', 'message': f'Error al actualizar stock: {str(ex)}'}, status=500)

        # Redirigir a la vista de ventas
        return redirect('ventas')

    except Exception as e:
        print(f"❌ ERROR INTERNO: {str(e)}")
        return JsonResponse({'status': 'error', 'message': f'Error interno: {str(e)}'}, status=500)
#-----------------------------------------------------------------------------------------

        # ?? **query a la vista**
        try:
            #Podes agregar mas condiciones al WHERE segun los filtros
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM v_movimientos_stock_compuesto \
                           WHERE id_empresa = %s ", [request.session['id_empresa']])  
            result = cursor.fetchall()
            cursor.close()            

        except DatabaseError as ex:
            print(f"? Error al ejecutar VISTA: {ex}")
            return JsonResponse({'status': 'error', 'message': f'Error al actualizar stock: {str(ex)}'}, status=500)
