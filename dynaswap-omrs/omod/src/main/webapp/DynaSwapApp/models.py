"""  DynaSwapApp/models.py  """
from django.db import models


class Roles(models.Model):
    """  OpenMRS role Class  """
    class Meta:
        db_table = "role"
    role = models.CharField(max_length=50, unique=True, primary_key=True)
    description = models.CharField(max_length=255)
    uuid = models.CharField(max_length=38)
    url = models.URLField(max_length=255)
    feature = models.BinaryField()

    def __str__(self):
        return self.role


class Users(models.Model):
    """  OpenMRS users Class  """
    class Meta:
        db_table = "users"
    user_id = models.IntegerField(unique=True, primary_key=True)
    username = models.CharField(max_length=50, unique=True)


class DynaSwapUsers(models.Model):
    """  dynaswap_users Class  """
    class Meta:
        db_table = "dynaswap_users"
    dynaswap_user_id = models.IntegerField(primary_key=True)
    role = models.CharField(max_length=50)
    bio_capsule = models.BinaryField()
    classifier = models.BinaryField()
    created_on = models.DateTimeField(auto_now=True)
    last_authenticated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.dynaswap_user_id


class UsersRoles(models.Model):
    """  OpenMRS user_role Class  """
    class Meta:
        db_table = "user_role"
    user_id = models.ForeignKey(
        Users, db_column="user_id", on_delete=models.CASCADE)
    role = models.ForeignKey(Roles, db_column="role", on_delete=models.CASCADE)

    def __str__(self):
        return self.user_id, self.role
