"""
URLs para la gestión de salas de estudio.

Define las rutas para salas, reservas y reseñas.

REQ-014: URLs de salas y reservas
"""

from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    # Listado y búsqueda de salas
    path('', views.room_list, name='room_list'),
    path('salas/', views.room_list, name='room_list_alt'),
    
    # Detalle de salas
    path('sala/<int:room_id>/', views.room_detail, name='room_detail'),
    
    # Reservas
    path('sala/<int:room_id>/reservar/', views.room_reserve, name='room_reserve'),
    path('sala/<int:room_id>/reservar/', views.room_reserve, name='reservation_create'),
    path('reservas/', views.reservation_list, name='reservation_list'),
    path('mis-reservas/', views.reservation_list, name='my_reservations'),
    path('reserva/<int:reservation_id>/', views.reservation_detail, name='reservation_detail'),
    path('reserva/<int:reservation_id>/cancelar/', views.reservation_cancel, name='reservation_cancel'),
    
    # Reseñas
    path('reserva/<int:reservation_id>/calificar/', views.room_review, name='room_review'),
    
    # URLs para administradores
    path('admin/sala/crear/', views.admin_room_create, name='room_create'),
    path('admin/sala/crear/', views.admin_room_create, name='admin_room_create'),
    path('admin/sala/<int:room_id>/editar/', views.admin_room_edit, name='admin_room_edit'),
    path('admin/reservas/', views.reservation_list, name='reservation_admin'),
    
    # API endpoints
    path('api/sala/<int:room_id>/disponibilidad/', views.api_room_availability, name='api_room_availability'),
]