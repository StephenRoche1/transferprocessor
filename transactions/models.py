from django.db import models


# Create your models here.
class Transaction(models.Model):
    id = models.IntegerField(primary_key=True)
    Source = models.CharField(max_length=3)
    Destination = models.CharField(max_length=3)
    Amount = models.DecimalField(max_digits=20000000,decimal_places=2)
    FX = models.DecimalField(max_digits=1000,decimal_places=2)
    DestinationAmount = models.DecimalField(max_digits=20000000,decimal_places=2)

    def __str__(self):
        return self.Source,self.Destination,
