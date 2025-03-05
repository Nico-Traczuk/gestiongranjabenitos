"""
URL configuration for benitos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from carniceria import views
from carniceria.views import *
from users.views import ViewLogin, ViewLogout, ViewErrorUsuario


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ViewLogin, name='login'),
    path('login/', ViewLogin, name='login'),
    path('logout/', ViewLogout, name='logout'),
    path('errorUsuario/', ViewErrorUsuario, name='errorUsuario'),
	# path('accounts/login/', ViewLogin, name='login'), 
    path('home/', views.Viewhome, name='home'),
    path('costos/', views.ViewCostos, name='costos'),
    path('costosTabla', views.ViewCostosTabla, name='costosTabla'),
    path('ventas/', views.Viewventas, name='ventas'),
    path('ventas/procesar_venta/', views.procesar_venta, name='procesar_venta'),  # <-- Agregar esta línea
    path('reporte/', views.Viewreportes, name='reporte'),
    path('reporteStockCompuesto/', views.ViewReporteCompuesto, name='reporteStockCompuesto'),
    path('stockCompuesto/', views.ViewStockCompuesto, name='stockCompuesto'),
    path('stockProducto/', views.ViewStockProducto, name='stockProducto'),
    path('get_producto_data/<int:id_articulo>/', get_producto_data, name='get_producto_data'),
    path('articulosSucursal', views.ViewArticulosSucursal, name='articulosSucursal'),
    path('agregar-articulo/', agregar_articulo, name='agregar_articulo'),
    path('quitar-articulo/', quitar_articulo, name='quitar_articulo'),
]
