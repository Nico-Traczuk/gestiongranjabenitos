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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.Viewhome, name='home'),
    path('stock/', views.Viewstock, name='stock'),
    path('ventas/', views.Viewventas, name='ventas'),
    path('reporte/', views.Viewreportes, name='reporte'),
    #Gestion es para todo lo que tiene que ver con ABM------------------------------------
    # path('gestionProductosCompuestos/', views.ViewGestionProductosCompuestos, name='gestionProductosCompuestos'),
    # path('gestionProductos/', views.ViewGestionProductos, name='gestionProductos'),
    path('stockCompuesto/', views.ViewStockCompuesto, name='stockCompuesto'),
    path('stockProducto/', views.ViewStockProducto, name='stockProducto'),

]
