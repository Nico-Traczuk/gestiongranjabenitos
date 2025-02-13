from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from users.templates import *
from users.models import User
#-----------------------------------------------------------
# CREAMOS LA VISTA DEL LOGIN CON UNA VERIFICACION PARA EL CUIT Y CONTRASEÑAfrom django.contrib.auth import authenticate, login


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
            print(f"✅ Usuario autenticado: {user}")
            print(f"   - ID Empresa: {getattr(user.id_empresa, 'id_empresa', 'No asignado')}")
            print(f"   - ID Sucursal: {getattr(user.id_sucursal, 'id_sucursal', 'No asignado')}")
            print(f"   - Tipo de usuario: {user.id_tipo_usuario}")

            login(request, user)

            # Redirigir según el tipo de usuario
            if user.id_tipo_usuario == 2:
                return redirect('/ventas/')
            elif user.id_tipo_usuario == 1:
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