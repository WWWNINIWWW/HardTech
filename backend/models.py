from django.db import models
from django.utils import timezone

class PC(models.Model):
    FAN_MODE_CHOICES = [
        (0, 'Desligado'),
        (1, 'Ligado'),
        (2, 'Automático'),
    ]
    
    user = models.CharField(max_length=255, unique=True)
    mode_fan = models.IntegerField(choices=FAN_MODE_CHOICES, default=0)
    update = models.BooleanField(default=False) # Nova coluna de update

class Dados(models.Model):
    pc = models.ForeignKey(PC, related_name='dados', on_delete=models.CASCADE)
    temperatura = models.DecimalField(default=0.00, decimal_places=2, max_digits=20)
    uso_CPU = models.DecimalField(default=0.00, decimal_places=2, max_digits=20)
    uso_RAM = models.DecimalField(default=0.00, decimal_places=2, max_digits=20)
    data_recebimento = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"PC: {self.pc.user}, Temperatura: {self.temperatura}, Uso CPU: {self.uso_CPU}, Uso RAM: {self.uso_RAM}, Data de Recebimento: {self.data_recebimento}"