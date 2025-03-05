from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from users.templates import *
from users.models import  *

#-----------------------------------------------------------
# CREAMOS LA VISTA DEL LOGIN CON UNA VERIFICACION PARA EL CUIT Y CONTRASEÑA


def ViewLogin(request):
    if request.method == 'POST':
        cuit = request.POST.get('cuit')
        password = request.POST.get('password')
        next_url = request.POST.get('next', 'home')  # URL por defecto: home

        print(f"\n🔹 Datos recibidos del formulario:")
        print(f"   - CUIT: {cuit}")
        print(f"   - Contraseña: {password}")
        print(f"   - Next URL: {next_url}")

        user = authenticate(request, username=cuit, password=password)

        if user is not None:
            login(request, user)  # Iniciar sesión del usuario

            # Obtener ID de empresa y sucursal desde las tablas relacionadas
            id_user = user.id_user
            id_empresa = usuario_empresa.objects.filter(id_user=user).values_list('id_empresa', flat=True).first()
            id_sucursal = usuario_sucursal.objects.filter(id_user=user).values_list('id_sucursal', flat=True).first()
            id_tipo_usuario = user.id_tipo_usuario  # Este sí está en User directamente
            first_name = user.first_name
            nombre_empresa = empresa.objects.filter(id_empresa=id_empresa).values_list('nombre_empresa', flat=True).first()
            print(f"✅ Usuario autenticado: {user}")
            print(f"   - ID Usuario: {id_user}")
            print(f"   - ID Empresa: {id_empresa if id_empresa else 'No asignado'}")
            print(f"   - ID Sucursal: {id_sucursal if id_sucursal else 'No asignado'}")
            print(f"   - Tipo de usuario: {id_tipo_usuario}")
            print(f"   - Nombre: {first_name}")
            print(f"   - Nombre de la empresa: {nombre_empresa}")
            # Guardar información en la sesión
            
            request.session['id_user'] = id_user
            request.session['id_empresa'] = id_empresa
            request.session['id_sucursal'] = id_sucursal
            request.session['id_tipo_usuario'] = id_tipo_usuario
            request.session['first_name'] = first_name
            request.session['nombre_empresa'] = nombre_empresa
            # Redirigir según el tipo de usuario
            if id_tipo_usuario == 2:
                return redirect('/ventas/')
            elif id_tipo_usuario == 1:
                return redirect('/home/')
            return redirect(next_url)

        else:
            print("❌ Error: CUIT o contraseña incorrectos.")
            messages.error(request, 'CUIT o contraseña incorrectos.')

    return render(request, 'login.html')

def ViewLogout(request):
    logout(request)  # Cierra la sesión del usuario
    return redirect('login')  # Redirige a la página de login (ajústalo según tu app)

def ViewErrorUsuario(request):
    return render(request, 'errorUsuario.html')