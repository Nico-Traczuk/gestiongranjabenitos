# ESTAMOS EN MODELOS DE USUARIO

from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from carniceria.models import *


# creamos el modelo usuario

class User(models.Model):
    id_user = models.AutoField(primary_key=True)
    cuit = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=128)  # Almacenamos contraseñas encriptadas
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    id_empresa = models.ForeignKey('carniceria.empresa', on_delete=models.CASCADE, default=1)
    id_sucursal = models.ForeignKey('carniceria.sucursales', on_delete=models.CASCADE, default=1)
    role = models.CharField(max_length=30)
    class Meta:
        db_table = "users"
        
    def set_password(self, password):
        self.password = make_password(password) #hasheamos la password + seguridad
    
    def check_password(self, password): #validamos la password
        return check_password(password, self.password)
        
