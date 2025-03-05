# ESTAMOS EN MODELOS DE USUARIO

from django.db import models
from carniceria.models import *
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password

class UserManager(BaseUserManager):
    def create_user(self, cuit, password=None, **extra_fields):
        """Crea un usuario con CUIT y contraseña"""
        if not cuit:
            raise ValueError("El CUIT es obligatorio")

        user = self.model(cuit=cuit, **extra_fields)
        user.password = make_password(password)  # Hashear la contraseña manualmente
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    id_user = models.AutoField(primary_key=True)
    cuit = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=128)  # Almacenamos la contraseña encriptada
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    id_tipo_usuario = models.IntegerField()  # ID como número
    is_active = models.BooleanField(default=True)  # Necesario para autenticación

    objects = UserManager()

    USERNAME_FIELD = 'cuit'  # Django usará CUIT en lugar de username
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = "users"

class usuario_empresa(models.Model):
    id_user = models.ForeignKey('users.User', on_delete=models.CASCADE, db_column='id_user')
    id_empresa = models.ForeignKey('carniceria.empresa', on_delete=models.CASCADE, db_column='id_empresa')
    
    class Meta:
        db_table = "usuario_empresa"

class usuario_sucursal(models.Model):
    id_user = models.ForeignKey('users.User', on_delete=models.CASCADE, db_column='id_user')
    id_empresa = models.ForeignKey('carniceria.empresa', on_delete=models.CASCADE, db_column='id_empresa')
    id_sucursal = models.ForeignKey('carniceria.sucursales', on_delete=models.CASCADE, db_column='id_sucursal')
    
    class Meta:
        db_table = "usuario_sucursal"