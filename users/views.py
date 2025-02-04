# ESTAMOS EN VIEWS DE USUARIOS

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .models import User


# CREAMOS NUESTRAS VISTAS
def ViewLogin(request):
    if request.method == "POST":
        cuit = request.POST.get('cuit')
        password = request.POST.get('password')

        try:
            user = User.objects.get(cuit=cuit)
            if user.check_password(password):  # Validamos la contraseña encriptada
                request.session['user_id'] = user.id_user  # Guardamos la sesión manualmente
                request.session['user_name'] = user.first_name
                return redirect('home')  # Redirigir al home
            else:
                messages.error(request, "Contraseña incorrecta")
        except User.DoesNotExist:
            messages.error(request, "El CUIT ingresado no existe")

    return render(request, 'login.html')