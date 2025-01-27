from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q
from .templates import *
from .models import *
from .forms import stockCompuestoForm, productosForm
from datetime import datetime, timedelta
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
#-----------------------------------------------------------------------------
def Viewhome(request):

	#HARDCODE LAS VARIABLES DE SESION (ID SUC, ID EMPRESA, ID USUARIO, ID TIPO USUARIO)
	request.session['id_sucursal'] = 1
	request.session['id_empresa'] = 1
	request.session['id_usuario'] = 1
	request.session['id_tipo_usuario'] = 1
	
	date = datetime.now().date


	return render(request, 'home.html', context={ 'date': date})




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
	
	# Pagination
	items_per_page = 10
	paginator = Paginator(productos, items_per_page)
	page = request.GET.get('page', 1)
	
	try:
		productos_paginados = paginator.page(page)
	except PageNotAnInteger:
		productos_paginados = paginator.page(1)
	except EmptyPage:
		productos_paginados = paginator.page(paginator.num_pages)
	
	return render(request, 'ventas.html', {
		'productos': productos_paginados,
		'search_query': search_query,
	})

#-----------------------------------------------------------------------------
def Viewreportes(request):
	productos = articulos.objects.all()
	#de acuerdo al usuario se tiene que renderizar la vista
	# id_tipo_usuario = request.session.get('id_tipo_usuario') 
	# #si 1 = administrador mostramos los reportes
	# if id_tipo_usuario == 1: 
	#     return render(request, 'reportes.html', context={'productos': productos})
	# else:
	return render(request, 'reportes.html', context={'productos': productos})

#-----------------------------------------------------------------------------
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
def Viewstock(request):
	# Session variables initialization
	id_sucursal = request.session.get('id_sucursal')
	id_empresa = request.session.get('id_empresa')
	id_usuario = request.session.get('id_usuario')
	id_tipo_usuario = request.session.get('id_tipo_usuario')
	
	# Initialize forms as None
	producto_form = None
	compuesto_form = None
	
	print(request.method)

	if request.method == 'POST':
		origen = request.POST.get('origen')
		method = request.POST.get('method')
		print(origen, method)
		
	#     if origen == 'ART':
	#         producto_form = productosForm(request.POST)
	#         if producto_form.is_valid():
	#             producto_form.save()
	#             return redirect('stock')
	#     elif origen == 'COMP':
	#         compuesto_form = stockCompuestoForm(request.POST)
	#         if compuesto_form.is_valid():
	#             compuesto_form.save()
	#             return redirect('stock')
	#     else:
	#         print("ERROR: Invalid origen in POST")
	#         return redirect('stock')
	
	
			
	elif request.method == 'DELETE':
		origen = request.GET.get('origen')
		method = request.GET.get('method')	#No hace falta evaluar esto ya que sabemos que es un DELETE con origen COMP/ART
		
		if origen == 'COMP':
			print("BORRANDO COMPUESTO")
		elif origen == 'ART':
			print("BORRANDO ARTICULO")
	#     # Django doesn't process PUT/DELETE body automatically
	#     # We need to parse it manually if you're sending as PUT/DELETE
	#     # Alternatively, you could use POST with a hidden _method field
		
	#     if request.method == 'DELETE':
	#         origen = request.GET.get('origen')
	#         try:
	#             if origen == 'ART':
	#                 id_art = request.GET.get('id_articulo')
	#                 articulo = articulos.objects.get(id_articulo=id_art)
	#                 articulo.delete()
	#                 return JsonResponse({'status': 'success'})
	#             elif origen == 'COMP':
	#                 id_stock_comp = request.GET.get('id_stock_compuesto')
	#                 stock_compuesto_obj = stock_compuesto.objects.get(
	#                     id_stock_compuesto=id_stock_comp
	#                 )
	#                 stock_compuesto_obj.delete()
	#                 return JsonResponse({'status': 'success'})
	#         except (articulos.DoesNotExist, stock_compuesto.DoesNotExist):
	#             return JsonResponse({'status': 'error'}, status=404)
		
	#     elif request.method == 'PUT':
	#         origen = request.GET.get('origen', id)
	#         try:
	#             if origen == 'ART':
	#                 id = request.GET.get('id_articulo')
	#                 articulo = articulos.objects.get(id_articulo=id)
	#                 form = productosForm(request.PUT, instance=articulo)
	#                 if form.is_valid():
	#                     form.save()
	#                     return JsonResponse({'status': 'success'})
	#             elif origen == 'COMP':
	#                 id_stock_comp = request.GET.get('id_stock_compuesto')
	#                 stock_compuesto_obj = stock_compuesto.objects.get(
	#                     id_stock_compuesto=id_stock_comp
	#                 )
	#                 form = stockCompuestoForm(request.PUT, instance=stock_compuesto_obj)
	#                 if form.is_valid():
	#                     form.save()
	#                     return JsonResponse({'status': 'success'})
	#         except (articulos.DoesNotExist, stock_compuesto.DoesNotExist):
	#             return JsonResponse({'status': 'error'}, status=404)
	
	
	# Formularios
	producto_form = productosForm()
	compuesto_form = stockCompuestoForm()
	
	# GET a los productos para mostrarlos
	productos = articulos.objects.all()  
	productosCompuestos = stock_compuesto.objects.all()
	
	# Pagination 
	paginator = Paginator(productos, 10)
	page = request.GET.get('page')
	
	try:
		productos_paginados = paginator.page(page)
	except PageNotAnInteger:
		productos_paginados = paginator.page(1)
	except EmptyPage:
		productos_paginados = paginator.page(paginator.num_pages)
	
	# Prepare context with all necessary data
	context = {
		'productos': productos_paginados,
		'productosCompuestos': productosCompuestos,
		'producto_form': producto_form,
		'compuesto_form': compuesto_form,
		'id_sucursal': id_sucursal,
		'id_empresa': id_empresa,
	}
	
	return render(request, 'stock.html', context)

