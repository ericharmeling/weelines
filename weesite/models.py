from django.db import models

class User(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=35)
    password = models.CharField(max_length=35)

class Position(models.Model):
    account = models.UUIDField()
    symbol = models.CharField(max_length=6)
    quantity = models.IntegerField()
    last_price = models.FloatField()
    last_total = models.FloatField()
    