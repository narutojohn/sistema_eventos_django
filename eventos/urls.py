from django.urls import path
from . import views
from .views import EventoListCreateAPIView 
from .views import EventoDetailAPIView

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    # Aquí agregaremos más rutas luego (eventos, editar, eliminar, etc.)
    path('eventos/', views.lista_eventos, name='lista_eventos'),
    path('eventos/crear/', views.crear_evento, name='crear_evento'),
    path('eventos/<int:evento_id>/editar/', views.editar_evento, name='editar_evento'),
    path('eventos/<int:evento_id>/eliminar/', views.eliminar_evento, name='eliminar_evento'),
    path('eventos/<int:evento_id>/clima/', views.ver_clima, name='ver_clima'),
    path('eventos/<int:evento_id>/registrar/', views.registrar_usuario_evento, name='registrar_usuario_evento'),
    path('eventos/<int:evento_id>/registrar_publico/', views.registrar_usuario_evento_publico, name='registrar_usuario_evento_publico'),
    path('api/clima/', views.api_clima, name='api_clima'),
    path('contacto/', views.contacto, name='contacto'),
    path('acerca/', views.acerca, name='acerca'),
    path('', views.inicio, name='inicio'),
    path('api/eventos/', EventoListCreateAPIView.as_view(), name='api_eventos_list_create'),
    path('api/eventos/<int:pk>/', EventoDetailAPIView.as_view(), name='api_evento_detail'),
    path('acceso_denegado/', views.acceso_denegado, name='acceso_denegado'),
]