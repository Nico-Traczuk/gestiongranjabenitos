# SCRIPT PARA CREAR USUARIOS

import django
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'benitos.settings')
django.setup()

# Importar modelos
from users.models import *
#from carniceria.models import sucursales, empresa  # Importa los modelos necesarios
from django.db import connection, transaction, DatabaseError

#en este modelo crear empresa, crear sucursal y crear usuario establecemos articulo empresa y tambien articulo sucursal
def create_user(cuit, password, first_name, last_name, id_tipo_usuario):
    """Crea un usuario en la base de datos con los valores proporcionados."""
    try:
        # Obtener instancias de las claves foráneas
        #sucursal_instance = usuario_sucursal.objects.get(id_sucursal=id_sucursal)
        #empresa_instance = usuario_empresa.objects.get(id_empresa=id_empresa)

        # Usamos el método create_user del manager para hashear la contraseña
        user = User.objects.create_user(
            cuit=cuit, 
            password=password,
            first_name=first_name, 
            last_name=last_name, 
#            id_sucursal=sucursal_instance,
#            id_empresa=empresa_instance,
            id_tipo_usuario=id_tipo_usuario
        )

        print(f"✅ Usuario {first_name} {last_name} creado exitosamente.")
#    except sucursales.DoesNotExist:
#        print(f"⚠️ Error: La sucursal con ID {id_sucursal} no existe.")
#    except empresa.DoesNotExist:
#        print(f"⚠️ Error: La empresa con ID {id_empresa} no existe.")
    except Exception as e:
        print(f"❌ Error: {e}")

# Lista de usuarios a crear
#usuarios = [
#    {
#        'cuit': '99999999999',
#        'password': '99999999999',
#        'first_name': ' Demo',
#        'last_name': ' Prueba',
#        # 'id_sucursal': 1,
#        # 'id_empresa': 99999999999,
#        'id_tipo_usuario': 1
#    }
#]

# Crear usuarios
#for usuario in usuarios:
#    create_user(**usuario) 

#print("✅ Todos los usuarios han sido creados correctamente.")

#Argumentos recibidos
try:
	cuit_empresa = sys.argv[1]
	id_sucursal = sys.argv[2]
	nombre = sys.argv[3]
	direccion = sys.argv[4]
	telefono = sys.argv[5]
	email = sys.argv[6]
	desc_sucursal = sys.argv[7]
	es_demo = sys.argv[8]
	crear_usuario = sys.argv[9]
	usr_first_name = sys.argv[10]
	usr_last_name = sys.argv[11]
	usr_cuit = sys.argv[12]
	usr_tipo_usuario = sys.argv[13]
except:
	print('>>>>> ERROR: Par�metros incorrectos (cuit_empresa id_sucursal "emp_nombre" "emp_direccion" "emp_telefono" "emp_email" "desc_sucursal" es_demo crear_usuario "usr_first_name" "usr_last_name" usr_cuit usr_tipo_usuario)')	print("------------------------------------------")
	print("Si crear_usuario = 'S': Se crea un usuario nuevo y ademas:")
	print("Si no existe cuit_empresa, creo todo de cero, sino, se evalua que se va a crear")
	print("Si id_sucursal = 0, pero cuit_empresa != '', se crea una sucursal para esa empresa")
	print("------------------------------------------")
	return

#Se crea el usuario primero
#id_usuario = create_user(cuit, password, first_name, last_name, id_tipo_usuario)

#Se ejecuta el SP
cursor = connection.cursor()
try:
	ret = cursor.execute("sp_nueva_empresa %s, %s, %s, %s, %s, %s, %s, %s, %s", [cuit_empresa, id_sucursal, id_usuario, nombre, direccion, telefono, email, desc_sucursal, es_demo])
except DatabaseError as err:
	print(err.args[1])

cursor.close()

