from django import forms
from .models import categorias, articulos, tipo_unidad, articulo_compuesto, stock_compuesto, gastos
from django.shortcuts import render, redirect

#------------------------------------------------------------------------------------------#

class articulo_compuestoForm(forms.ModelForm):
    class Meta:
        #LE TIENE QUE LLEGAR EL ID UNICO DE REGISTRO PARA QUE DJANGO HAGA UN UPDATE O DELETE!!!!
        model = articulo_compuesto
        fields = ('descripcion', 'id_categoria', 'id_unidad')
        labels = {
            'descripcion': 'Descripcion',
            'id_categoria': 'Categoria',
            'id_unidad': 'Tipo de Unidad',
        }
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control w-1/4 ml-5 my-3 px-4 py-2 rounded-md focus:outline-none focus:shadow-outline', 'placeholder': 'Ingrese una Descripcion'}),
            'id_categoria': forms.Select(attrs={'class': 'form-control capitalize w-1/4 ml-5 my-3 px-4 py-2 rounded-md focus:outline-none focus:shadow-outline', 'placeholder': 'Ingrese una Categoria'}),
            'id_unidad': forms.Select(attrs={'class': 'form-control capitalize w-1/4 ml-5 px-4 my-3 py-2 rounded-md focus:outline-none focus:shadow-outline', 'placeholder': 'Ingrese el Tipo de Unidad'}),
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = categorias
        fields = ('id_categoria', 'categoria')

#------------------------------------------------------------------------------------------#

class stockCompuestoForm(forms.ModelForm):
    class Meta:
        #LE TIENE QUE LLEGAR EL ID UNICO DE REGISTRO PARA QUE DJANGO HAGA UN UPDATE O DELETE!!!!
        model = stock_compuesto
        fields = ( 'id_stock_compuesto','id_compuesto', 'peso_inicial')
        labels = {
            'id_compuesto': 'Descripcion',

            'peso_inicial': 'Peso Inicial',

        }
        widgets = {
            'id_stock_compuesto': forms.HiddenInput(),
            'id_compuesto': forms.Select(attrs={'class': 'form-control w-1/4 ml-5 my-3 px-4 py-2 rounded-md focus:outline-none focus:shadow-outline', 'placeholder': 'Ingrese una Descripcion'}),
           
            'peso_inicial': forms.NumberInput(attrs={'class': 'form-control w-1/4 ml-5 my-3 px-4 py-2 rounded-md focus:outline-none focus:shadow-outline', 'placeholder': 'Ingrese un Peso Inicial'}),
        }
            

#------------------------------------------------------------------------------------------#
class productosForm(forms.ModelForm):
    class Meta:
        #LE TIENE QUE LLEGAR EL ID UNICO DE REGISTRO PARA QUE DJANGO HAGA UN UPDATE O DELETE!!!!
        model = articulos
        fields = ('id_articulo','id_unidad', 'id_categoria', 'codigo_articulo', 'descripcion', 'precio_costo', 'precio_venta')
        labels = {
            'id_unidad': 'Tipo de Unidad',
            'id_categoria': 'Categoria',
            'codigo_articulo': 'Codigo',
            'descripcion': 'Descripcion',
            'precio_costo': 'Precio de Costo',
            'precio_venta': 'Precio de Venta',
        }
        widgets = {
            'id_articulo': forms.HiddenInput(),
            'id_unidad': forms.Select( 
                attrs={'class': ' form-control capitalize ml-5 px-4 w-1/2 my-2 py-2 rounded-md focus:outline-none shadow-lg focus:shadow-outline'}
            ),
            'id_categoria': forms.Select(attrs={'class': 'form-control capitalize w-1/2  ml-5 px-4 my-2 py-2 rounded-md focus:outline-none shadow-lg focus:shadow-outline', 'placeholder': 'Ingrese una Categoria'}),
            'codigo_articulo': forms.TextInput(attrs={'class': 'form-control w-1/2  ml-5 px-4 my-2 py-2 rounded-md focus:outline-none shadow-lg focus:shadow-outline bg-gray-200' , 'placeholder': 'Ingrese un Codigo'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control w-1/2  ml-5 px-4 my-2 py-2 rounded-md focus:outline-none shadow-lg focus:shadow-outline bg-gray-200', 'placeholder': 'Ingrese una Descripcion'}),
            'precio_costo': forms.NumberInput(attrs={'class': 'form-control w-1/2  ml-5 px-4 my-2 py-2 rounded-md focus:outline-none shadow-lg focus:shadow-outline bg-gray-200', 'placeholder': 'Ingrese un Precio de Costo'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control  w-1/2 ml-5 px-4 my-2 py-2 rounded-md focus:outline-none shadow-lg focus:shadow-outline bg-gray-200', 'placeholder': 'Ingrese un Precio de Venta'}),
        }

#------------------------------------------------------------------------------------------#


class gastosForm(forms.ModelForm):
    class Meta:
        model = gastos
        fields = ('id_gasto','id_empresa', 'id_sucursal', 'fecha_gasto', 'descripcion', 'monto')
        labels = {
            'id_empresa': 'Empresa',
            'id_sucursal': 'Sucursal',
            'fecha_gasto': 'Fecha',
            'descripcion': 'Descripcion',
            'monto': 'Monto',
        }
        widgets = {
            'id_gasto': forms.HiddenInput(),
            'id_empresa': forms.Select( 
                attrs={'class': ' form-control capitalize ml-5 px-4   my-2 py-2 rounded-md focus:outline-none shadow-lg focus:shadow-outline'}
            ),
            'id_sucursal': forms.Select( 
                attrs={'class': ' form-control capitalize ml-5 px-4   my-2 py-2 rounded-md focus:outline-none shadow-lg focus:shadow-outline'}  
            ),
            'fecha_gasto': forms.DateInput(
                attrs={'class': 'form-control    ml-5 px-4 my-2 py-2 rounded-md focus:outline-none shadow-lg focus:shadow-outline bg-gray-200', 'type': 'date', 'format': '%d %B %Y'}
            ),
            'descripcion': forms.TextInput(
                attrs={'class': 'form-control col-span-3  ml-5 px-4 my-2 py-2 rounded-md focus:outline-none shadow-lg focus:shadow-outline bg-gray-200', 'placeholder': 'Ingrese una Descripcion'}
            ),
            'monto': forms.NumberInput(
                attrs={'class': 'form-control    ml-5 px-4 my-2 py-2 rounded-md focus:outline-none shadow-lg focus:shadow-outline bg-gray-200', 'placeholder': 'Ingrese un Monto'}
            ),
            
        }

