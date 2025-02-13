# SCRIPT PARA CREAR USUARIOS

import django
import os

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'benitos.settings')
django.setup()

# Importar modelos
from users.models import User
from carniceria.models import sucursales, empresa  # Importa los modelos necesarios

def create_user(cuit, password, first_name, last_name, id_sucursal, id_empresa, id_tipo_usuario):
    """Crea un usuario en la base de datos con los valores proporcionados."""
    try:
        # Obtener instancias de las claves foráneas
        sucursal_instance = sucursales.objects.get(id_sucursal=id_sucursal)
        empresa_instance = empresa.objects.get(id_empresa=id_empresa)

        # Usamos el método create_user del manager para hashear la contraseña
        user = User.objects.create_user(
            cuit=cuit, 
            password=password,
            first_name=first_name, 
            last_name=last_name, 
            id_sucursal=sucursal_instance,
            id_empresa=empresa_instance,
            id_tipo_usuario=id_tipo_usuario
        )

        print(f"✅ Usuario {first_name} {last_name} creado exitosamente.")
    except sucursales.DoesNotExist:
        print(f"⚠️ Error: La sucursal con ID {id_sucursal} no existe.")
    except empresa.DoesNotExist:
        print(f"⚠️ Error: La empresa con ID {id_empresa} no existe.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

# Lista de usuarios a crear
usuarios = [
    {
        'cuit': '20349458451',
        'password': 'minombre1992',
        'first_name': 'Nicolas',
        'last_name': 'Traczuk',
        'id_sucursal': 1,
        'id_empresa': 1,
        'id_tipo_usuario': 2
    }
]

# Crear usuarios
for usuario in usuarios:
    create_user(**usuario) 

print("✅ Todos los usuarios han sido creados correctamente.")
