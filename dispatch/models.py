import re
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from dispatch.choices import MODEL_CHOICES, STATE_CHOICES

# Create your models here.

class Drone(models.Model):
    serial_number = models.CharField(max_length=100, unique=True)
    model = models.CharField(max_length=20, choices=MODEL_CHOICES)
    weight_limit = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(500)])
    battery_capacity = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default="IDLE")
    
    def __str__(self):
        return f"{self.serial_number} - {self.model} - {self.state}"
    
    
class Medication(models.Model):
    name = models.CharField(max_length=255)
    weight = models.FloatField()
    code = models.CharField(max_length=100)
    image = models.ImageField(upload_to='medications/')
    drone = models.ForeignKey(Drone, related_name='medications', on_delete=models.CASCADE)

    def clean(self):
        if not re.match(r'^[A-Za-z0-9_-]+$', self.name):
            raise ValidationError('Invalid name')
        if not re.match(r'^[A-Z0-9_]+$', self.code):
            raise ValidationError('Invalid code')
        
    def __str__(self):
        return self.name