from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from functools import wraps

def user_type_required(*tipo_usuario_permitido):
    def decorator(view_func):
        @wraps(view_func)  # Mantiene el nombre y los atributos de la función original
        def _wrapped_view(request, *args, **kwargs):
            # Verifica si el usuario está autenticado
            if not request.user.is_authenticated:
                return redirect(f'/login/?next={request.path}')  # Redirige a login con la URL original

            # Obtiene el tipo de usuario directamente del modelo User
            tipo_usuario = getattr(request.user, 'id_tipo_usuario', None)
            
            if tipo_usuario in tipo_usuario_permitido:
                return view_func(request, *args, **kwargs)

            # Redirige a otra pantalla en lugar de devolver 403 Forbidden
            return redirect('/errorUsuario')

        return _wrapped_view
    return decorator




          
