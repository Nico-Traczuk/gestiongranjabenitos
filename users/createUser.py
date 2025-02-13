# SCRIPT PARA CREAR USUARIOS

import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'benitos.settings')
django.setup()

from users.models import User

def create_user(cuit, password, first_name, last_name, id_sucursal, id_empresa, role, ):
    user = User(
        cuit=cuit, 
        first_name=first_name, 
        last_name=last_name, 
        id_sucursal=id_sucursal,
        id_empresa=id_empresa,
        role=role
    )
    user.set_password(password)
    user.save()
    print ("Usuario creado exitosamente")
    
usuarios = [
    {
        'cuit': '20349458451',
        'password': 'minombre1992',
        'first_name': 'Nicolas',
        'last_name': 'Traczuk',
        'id_sucursal': 1,
        'id_empresa': 1,
        'role': 'admin'
    }
]

for usuario in usuarios:
    create_user(**usuario)
    
