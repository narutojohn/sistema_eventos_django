from rest_framework import serializers
from .models import Evento

class EventoSerializer(serializers.ModelSerializer):
    creador = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Evento
        fields = '__all__'
       
