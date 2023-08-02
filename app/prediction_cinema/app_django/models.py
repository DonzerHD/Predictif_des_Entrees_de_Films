from django.db import models


class Utilisateurs(models.Model):

    class Meta:
        managed = False
        db_table = 'Utilisateurs'
