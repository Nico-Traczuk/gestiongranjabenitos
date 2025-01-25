from django import forms
from .models import categorias, articulos, tipo_unidad, articulo_compuesto, stock_compuesto
from django.shortcuts import render, redirect


class articulo_compuestoForm(forms.ModelForm):
    class Meta:
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


class stockCompuestoForm(forms.ModelForm):
    class Meta:
        model = stock_compuesto
        fields = ('id_compuesto', 'cantidad_ingresada', 'peso_inicial')
        labels = {
            'id_compuesto': 'Descripcion',
            'cantidad_ingresada': 'Cantidad Ingresada',
            'peso_inicial': 'Peso Inicial',

        }
        widgets = {
            'id_compuesto': forms.Select(attrs={'class': 'form-control w-1/4 ml-5 my-3 px-4 py-2 rounded-md focus:outline-none focus:shadow-outline', 'placeholder': 'Ingrese una Descripcion'}),
            'cantidad_ingresada': forms.NumberInput(attrs={'class': 'form-control w-1/4 ml-5 my-3 px-4 py-2 rounded-md focus:outline-none focus:shadow-outline', 'placeholder': 'Ingrese una Cantidad Ingresada'}),
            'peso_inicial': forms.NumberInput(attrs={'class': 'form-control w-1/4 ml-5 my-3 px-4 py-2 rounded-md focus:outline-none focus:shadow-outline', 'placeholder': 'Ingrese un Peso Inicial'}),
        }
            


class productosForm(forms.ModelForm):
    class Meta:
        model = articulos
        fields = ('id_unidad', 'id_categoria', 'codigo_articulo', 'descripcion', 'precio_costo', 'precio_venta')
        labels = {
            'id_unidad': 'Tipo de Unidad',
            'id_categoria': 'Categoria',
            'codigo_articulo': 'Codigo',
            'descripcion': 'Descripcion',
            'precio_costo': 'Precio de Costo',
            'precio_venta': 'Precio de Venta',
        }
        widgets = {
            'id_unidad': forms.Select( 
                attrs={'class': 'form-control capitalize w-1/4 ml-5 px-4 my-2 py-2 rounded-md focus:outline-none focus:shadow-outline'}
            ),
            'id_categoria': forms.Select(attrs={'class': 'form-control capitalize w-1/4 ml-5 px-4 my-2 py-2 rounded-md focus:outline-none focus:shadow-outline', 'placeholder': 'Ingrese una Categoria'}),
            'codigo_articulo': forms.TextInput(attrs={'class': 'form-control w-1/4 ml-5 px-4 my-2 py-2 rounded-md focus:outline-none focus:shadow-outline', 'placeholder': 'Ingrese un Codigo'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control w-1/4 ml-5 px-4 my-2 py-2 rounded-md focus:outline-none focus:shadow-outline', 'placeholder': 'Ingrese una Descripcion'}),
            'precio_costo': forms.NumberInput(attrs={'class': 'form-control w-1/4 ml-5 px-4 my-2 py-2 rounded-md focus:outline-none focus:shadow-outline', 'placeholder': 'Ingrese un Precio de Costo'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control w-1/4 ml-5 px-4 my-2 py-2 rounded-md focus:outline-none focus:shadow-outline', 'placeholder': 'Ingrese un Precio de Venta'}),
        }



