

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Evento(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha = models.DateTimeField()
    ubicacion = models.CharField(max_length=200)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    creador = models.ForeignKey(User, on_delete=models.CASCADE)
    participantes = models.ManyToManyField(User, related_name="eventos_registrados", blank=True)  # 👈 ESTA ES LA NUEVA LÍNEA
    imagen = models.ImageField(upload_to='eventos/', null=True, blank=True)
    def __str__(self):
        return self.titulo
    
    #registro del usuario
class RegistroPublico(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='registros_publicos')
    class Meta:
        unique_together = ('correo', 'evento')  # Evita registros duplicados para un mismo evento

    def __str__(self):
        return f"{self.nombre} - {self.correo} - {self.evento.titulo}"
