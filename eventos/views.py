
# Create your views here.
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegistroUsuarioForm
from django.contrib.auth.decorators import login_required
from .models import Evento
from .forms import EventoForm
from django.shortcuts import get_object_or_404
import requests
from django.contrib import messages
#para registro usuario sin login
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.mail import send_mail
from django.conf import settings
from .models import RegistroPublico
from django.contrib.auth.decorators import user_passes_test
from rest_framework import generics, permissions
from .serializers import EventoSerializer


def registro(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)  # Inicia sesión automáticamente
            return redirect('lista_eventos')  # Redirige a la lista de eventos
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def lista_eventos(request):
    eventos = Evento.objects.all().prefetch_related('registros_publicos')

    registros_por_evento = {}
    for evento in eventos:
        registros_por_evento[evento.id] = list(evento.registros_publicos.all())

    return render(request, 'eventos/lista_eventos.html', {
        'eventos': eventos,
        'registros_por_evento': registros_por_evento,
    })



def acceso_denegado(request):
    return render(request, 'eventos/acceso_denegado.html', {'mensaje': 'No tienes permisos para acceder a esta sección.'})

def es_organizador(user):
   return user.is_authenticated and user.groups.filter(name='Organizadores').exists()



@login_required
@user_passes_test(es_organizador, login_url='acceso_denegado')
def crear_evento(request):
    if request.method == 'POST':
        form = EventoForm(request.POST,  request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.creador = request.user
            evento.save()
            return redirect('lista_eventos')
    else:
        form = EventoForm()
    return render(request, 'eventos/crear_evento.html', {'form': form})


@login_required
@user_passes_test(es_organizador, login_url='acceso_denegado')
def editar_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            return redirect('lista_eventos')
    else:
        form = EventoForm(instance=evento)
    return render(request, 'eventos/editar_evento.html', {'form': form})


@login_required
@user_passes_test(es_organizador, login_url='acceso_denegado')
def eliminar_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        evento.delete()
        return redirect('lista_eventos')
    return render(request, 'eventos/eliminar_evento.html', {'evento': evento})
@login_required
def ver_clima(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id, creador=request.user)

    # Paso 1: Convertir dirección a coordenadas usando Nominatim
    try:
        geocoding_url = f"https://nominatim.openstreetmap.org/search"
        params = {
            'q': evento.ubicacion,
            'format': 'json'
        }
        georesp = requests.get(geocoding_url, params=params, headers={'User-Agent': 'eventos-app'})
        geodata = georesp.json()

        if not geodata:
            messages.error(request, "No se pudieron obtener coordenadas para esta ubicación.")
            return redirect('lista_eventos')

        lat = geodata[0]["lat"]
        lon = geodata[0]["lon"]

    except Exception as e:
        messages.error(request, "Error al obtener coordenadas de la ubicación.")
        return redirect('lista_eventos')

    # Paso 2: Consultar API del clima con coordenadas obtenidas
    try:
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current_weather=true"
        )
        response = requests.get(weather_url)
        data = response.json()
        clima = data.get("current_weather", {})
    except Exception as e:
        clima = {}
        messages.error(request, "No se pudo obtener la información del clima.")

    return render(request, 'eventos/ver_clima.html', {
        'evento': evento,
        'clima': clima
    })

@login_required
@require_POST
def registrar_usuario_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    usuario = request.user

    if evento.participantes.filter(id=usuario.id).exists():
        return JsonResponse({'status': 'error', 'message': 'Ya estás registrado en este evento.'})

    evento.participantes.add(usuario)
    evento.save()

    return JsonResponse({'status': 'success', 'message': 'Te has registrado correctamente en el evento.'})
def inicio(request):
    eventos = Evento.objects.all()
    return render(request, 'eventos/inicio.html', {'eventos': eventos})

#para resgistar usuario sin login
@csrf_exempt
@require_POST
def registrar_usuario_evento_publico(request, evento_id):
    try:
        data = json.loads(request.body)
        nombre = data.get('nombre')
        correo = data.get('correo')

        if not nombre or not correo:
            return JsonResponse({'status': 'error', 'message': 'Nombre y correo son obligatorios.'})

        evento = get_object_or_404(Evento, id=evento_id)

        # Validar si ya está registrado
        existe = RegistroPublico.objects.filter(correo=correo, evento=evento).exists()
        if existe:
            return JsonResponse({'status': 'error', 'message': 'Este correo ya está registrado en el evento.'})

        # Guardar registro
        RegistroPublico.objects.create(nombre=nombre, correo=correo, evento=evento)

        # Enviar correo de confirmación
        asunto = f"Confirmación de registro al evento {evento.titulo}"
        mensaje = (
            f"Hola {nombre},\n\n"
            f"Has sido registrado correctamente en el evento:\n"
            f"Título: {evento.titulo}\n"
            f"Fecha: {evento.fecha.strftime('%d %b %Y %H:%M')}\n"
            f"Ubicación: {evento.ubicacion}\n\n"
            "¡Gracias por tu interés!"
        )
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [correo],
            fail_silently=False,
        )

        return JsonResponse({'status': 'success', 'message': 'Registro exitoso. Revisa tu correo para confirmación.'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Error al procesar el registro.'})
    


def api_clima(request):
    ubicacion = request.GET.get('ubicacion')
    if not ubicacion:
        return JsonResponse({'error': 'No se proporcionó ubicación.'})

    try:
        # Convertir ubicación a coordenadas
        geocoding_url = "https://nominatim.openstreetmap.org/search"
        params = {'q': ubicacion, 'format': 'json'}
        georesp = requests.get(geocoding_url, params=params, headers={'User-Agent': 'eventos-app'})
        geodata = georesp.json()

        if not geodata:
            return JsonResponse({'error': 'No se encontraron coordenadas para la ubicación.'})

        lat = geodata[0]['lat']
        lon = geodata[0]['lon']
    except:
        return JsonResponse({'error': 'Error al obtener coordenadas.'})

    try:
        # Obtener clima actual
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_resp = requests.get(weather_url)
        weather_data = weather_resp.json()
        current_weather = weather_data.get('current_weather')

        if not current_weather:
            return JsonResponse({'error': 'No se pudo obtener el clima actual.'})

        temperatura = current_weather.get('temperature')
        weather_code = current_weather.get('weathercode')

        # Mapear código de clima a descripción e ícono
        weather_map = {
            0: ("Despejado", "wi-day-sunny"),
            1: ("Mayormente despejado", "wi-day-sunny-overcast"),
            2: ("Parcialmente nublado", "wi-day-cloudy"),
            3: ("Nublado", "wi-cloudy"),
            45: ("Niebla", "wi-fog"),
            48: ("Niebla con escarcha", "wi-fog"),
            51: ("Llovizna ligera", "wi-sprinkle"),
            53: ("Llovizna moderada", "wi-showers"),
            55: ("Llovizna intensa", "wi-rain"),
            61: ("Lluvia ligera", "wi-raindrops"),
            63: ("Lluvia moderada", "wi-rain"),
            65: ("Lluvia fuerte", "wi-rain-wind"),
            71: ("Nieve ligera", "wi-snow"),
            73: ("Nieve moderada", "wi-snow-wind"),
            75: ("Nieve intensa", "wi-snowflake-cold"),
            95: ("Tormenta", "wi-thunderstorm"),
            96: ("Tormenta con granizo", "wi-storm-showers"),
            99: ("Tormenta severa", "wi-hurricane")
        }

        descripcion, icono_clase = weather_map.get(weather_code, ("Clima desconocido", "wi-na"))

        return JsonResponse({
            'temperatura': temperatura,
            'descripcion': descripcion,
            'icono': icono_clase
        })

    except:
        return JsonResponse({'error': 'Error al obtener datos del clima.'})

def contacto(request):
    return render(request, 'eventos/contacto.html')

def acerca(request):
    return render(request, 'eventos/acerca.html')

from rest_framework import permissions

class EventoListCreateAPIView(generics.ListCreateAPIView):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creador=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        eventos_data = serializer.data

        eventos_con_clima = []
        for evento, data in zip(queryset, eventos_data):
            clima = self.obtener_clima_para_ubicacion(evento.ubicacion)
            data['clima'] = clima
            eventos_con_clima.append(data)

        return JsonResponse(eventos_con_clima, safe=False)

    def obtener_clima_para_ubicacion(self, ubicacion):
        try:
            geocoding_url = "https://nominatim.openstreetmap.org/search"
            params = {'q': ubicacion, 'format': 'json'}
            georesp = requests.get(geocoding_url, params=params, headers={'User-Agent': 'eventos-app'})
            geodata = georesp.json()

            if not geodata:
                return {'error': 'No se encontraron coordenadas'}

            lat = geodata[0]['lat']
            lon = geodata[0]['lon']

            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            weather_resp = requests.get(weather_url)
            weather_data = weather_resp.json()
            current_weather = weather_data.get('current_weather')

            if not current_weather:
                return {'error': 'No se pudo obtener el clima'}

            return {
                'temperatura': current_weather.get('temperature'),
                'descripcion': self.descripcion_clima(current_weather.get('weathercode'))
            }

        except Exception as e:
            return {'error': 'Error al obtener clima'}

    def descripcion_clima(self, weather_code):
        weather_map = {
            0: "Despejado",
            1: "Mayormente despejado",
            2: "Parcialmente nublado",
            3: "Nublado",
            45: "Niebla",
            48: "Niebla con escarcha",
            51: "Llovizna ligera",
            53: "Llovizna moderada",
            55: "Llovizna intensa",
            61: "Lluvia ligera",
            63: "Lluvia moderada",
            65: "Lluvia fuerte",
            71: "Nieve ligera",
            73: "Nieve moderada",
            75: "Nieve intensa",
            95: "Tormenta",
            96: "Tormenta con granizo",
            99: "Tormenta severa"
        }
        return weather_map.get(weather_code, "Clima desconocido")

class EventoDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        clima = self.obtener_clima_para_ubicacion(instance.ubicacion)
        data['clima'] = clima

        return JsonResponse(data)

    def obtener_clima_para_ubicacion(self, ubicacion):
        try:
            geocoding_url = "https://nominatim.openstreetmap.org/search"
            params = {'q': ubicacion, 'format': 'json'}
            georesp = requests.get(geocoding_url, params=params, headers={'User-Agent': 'eventos-app'})
            geodata = georesp.json()

            if not geodata:
                return {'error': 'No se encontraron coordenadas'}

            lat = geodata[0]['lat']
            lon = geodata[0]['lon']

            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            weather_resp = requests.get(weather_url)
            weather_data = weather_resp.json()
            current_weather = weather_data.get('current_weather')

            if not current_weather:
                return {'error': 'No se pudo obtener el clima'}

            return {
                'temperatura': current_weather.get('temperature'),
                'descripcion': self.descripcion_clima(current_weather.get('weathercode'))
            }

        except Exception:
            return {'error': 'Error al obtener clima'}

    def descripcion_clima(self, weather_code):
        weather_map = {
            0: "Despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado", 3: "Nublado",
            45: "Niebla", 48: "Niebla con escarcha", 51: "Llovizna ligera", 53: "Llovizna moderada",
            55: "Llovizna intensa", 61: "Lluvia ligera", 63: "Lluvia moderada", 65: "Lluvia fuerte",
            71: "Nieve ligera", 73: "Nieve moderada", 75: "Nieve intensa", 95: "Tormenta",
            96: "Tormenta con granizo", 99: "Tormenta severa"
        }
        return weather_map.get(weather_code, "Clima desconocido")

    