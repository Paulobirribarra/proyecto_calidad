"""
Formularios para la gestión de salas y reservas.

Este módulo contiene formularios con validaciones personalizadas
para garantizar la integridad de los datos del sistema.

REQ-007: Validación de entradas y salidas
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Room, Reservation, Review


class MultipleRoleWidget(forms.CheckboxSelectMultiple):
    """Widget personalizado para seleccionar múltiples roles."""
    
    def __init__(self, attrs=None):
        # Definir opciones de roles
        choices = [
            ('admin', 'Administrador'),
            ('profesor', 'Profesor'),
            ('estudiante', 'Estudiante'),
            ('soporte', 'Soporte Técnico'),
        ]
        super().__init__(attrs, choices)


class RoleField(forms.MultipleChoiceField):
    """Campo personalizado para manejar roles múltiples."""
    
    def __init__(self, *args, **kwargs):
        # Definir opciones de roles
        choices = [
            ('admin', 'Administrador'),
            ('profesor', 'Profesor'),
            ('estudiante', 'Estudiante'),
            ('soporte', 'Soporte Técnico'),
        ]
        kwargs['choices'] = choices
        kwargs['widget'] = MultipleRoleWidget()
        kwargs['required'] = True
        super().__init__(*args, **kwargs)
    
    def clean(self, value):
        """Limpiar y validar los roles seleccionados."""
        if not value:
            raise ValidationError("Debe seleccionar al menos un rol permitido.")
        
        # Convertir lista a string separado por comas
        cleaned_value = super().clean(value)
        return ','.join(cleaned_value)


class RoomForm(forms.ModelForm):
    """
    Formulario para crear y editar salas.
    
    Incluye validaciones personalizadas para asegurar
    la integridad de los datos de la sala.
    """
      # Campo personalizado para roles permitidos
    allowed_roles = RoleField(
        label="Roles Permitidos *",
        help_text="Selecciona los tipos de usuario que pueden reservar esta sala"
    )
    
    class Meta:
        model = Room
        fields = [
            'name', 'description', 'capacity', 'equipment',
            'location', 'opening_time', 'closing_time',
            'room_type', 'allowed_roles'
        ]
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe las características y equipamiento de la sala...'
            }),
            'equipment': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ej: Proyector, Pizarra, Aire acondicionado, WiFi...'
            }),
            'opening_time': forms.TimeInput(attrs={'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time'}),
            'room_type': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si estamos editando una sala existente, cargar los roles actuales
        if self.instance and self.instance.pk and self.instance.allowed_roles:
            current_roles = [role.strip() for role in self.instance.allowed_roles.split(',')]
            self.initial['allowed_roles'] = current_roles
    
    def clean_name(self):
        """Validar nombre único de sala."""
        name = self.cleaned_data.get('name')
        
        if name:
            # Verificar si existe otra sala con el mismo nombre
            existing_room = Room.objects.filter(name__iexact=name)
            if self.instance.pk:
                existing_room = existing_room.exclude(pk=self.instance.pk)
            
            if existing_room.exists():
                raise ValidationError(
                    f"Ya existe una sala con el nombre '{name}'"
                )
        
        return name
    
    def clean_capacity(self):
        """Validar capacidad de la sala."""
        capacity = self.cleaned_data.get('capacity')
        if capacity is not None:
            if capacity < 1:
                raise ValidationError("La capacidad debe ser al menos 1 persona")
            if capacity > 100:
                raise ValidationError("La capacidad máxima permitida es 100 personas")
        
        return capacity
    
    def clean_allowed_roles(self):
        """Validar roles permitidos."""
        allowed_roles = self.cleaned_data.get('allowed_roles')
        
        if allowed_roles:
            # Si ya es una cadena (viene del campo personalizado), está validada
            if isinstance(allowed_roles, str):
                return allowed_roles
            
            # Si es una lista, procesarla
            if isinstance(allowed_roles, list):
                # Roles válidos en el sistema
                valid_roles = ['admin', 'profesor', 'estudiante', 'soporte']
                
                # Verificar que todos los roles sean válidos
                invalid_roles = [role for role in allowed_roles if role not in valid_roles]
                
                if invalid_roles:
                    raise ValidationError(
                        f"Roles inválidos: {', '.join(invalid_roles)}. "
                        f"Roles válidos: {', '.join(valid_roles)}"
                    )
                
                # Eliminar duplicados y reformatear
                unique_roles = list(dict.fromkeys(allowed_roles))  # Mantener orden
                return ','.join(unique_roles)
        
        return allowed_roles

    def clean(self):
        """Validación cruzada de campos."""
        cleaned_data = super().clean()
        opening_time = cleaned_data.get('opening_time')
        closing_time = cleaned_data.get('closing_time')
        
        if opening_time and closing_time:
            if opening_time >= closing_time:
                raise ValidationError(
                    "La hora de apertura debe ser anterior a la hora de cierre"
                )
            
            # Validar horarios razonables (entre 6 AM y 11 PM)
            if opening_time.hour < 6:
                raise ValidationError(
                    "La hora de apertura no puede ser antes de las 6:00 AM"
                )
            
            if closing_time.hour > 23:
                raise ValidationError(
                    "La hora de cierre no puede ser después de las 11:00 PM"
                )
        
        return cleaned_data


class ReservationForm(forms.ModelForm):
    """
    Formulario para crear y editar reservas.
    
    Incluye validaciones complejas para evitar conflictos
    de horarios y asegurar reservas válidas.
    """
    
    class Meta:
        model = Reservation
        fields = [
            'room', 'start_time', 'end_time', 
            'purpose', 'attendees_count', 'notes'
        ]
        widgets = {
            'start_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),            'purpose': forms.TextInput(attrs={
                'placeholder': 'Ej: Sesión de estudio grupal, Reunión de proyecto...',
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Información adicional sobre la reserva...',
                'class': 'form-control'
            }),            'attendees_count': forms.NumberInput(attrs={
                'min': '1',
                'class': 'form-control',
                'maxlength': '4',  # Máximo 4 dígitos (hasta 9999)
                'pattern': '[0-9]{1,4}',  # Solo números de 1 a 4 dígitos
                'title': 'Ingrese un número entre 1 y la capacidad de la sala (máximo 4 dígitos)',
                'oninput': 'this.value = this.value.slice(0, 4)'  # Limitar a 4 caracteres
            })
        }
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.room = kwargs.pop('room', None)  # Para poder establecer límites específicos por sala
        super().__init__(*args, **kwargs)
        
        # Filtrar solo salas activas
        self.fields['room'].queryset = Room.objects.filter(is_active=True)
          # Si tenemos una sala específica, establecer el límite máximo de asistentes
        if self.room:
            self.fields['attendees_count'].widget.attrs.update({
                'max': str(self.room.capacity),
                'data-capacity': str(self.room.capacity),
                'maxlength': '3',  # Máximo 3 dígitos
                'pattern': f'[0-9]{{1,{len(str(self.room.capacity))}}}',  # Patrón dinámico según capacidad
                'title': f'Ingrese un número entre 1 y {self.room.capacity}'
            })
        
        # NO establecer límites HTML5 para datetime - solo usar validación del servidor
        # Esto evita problemas de zona horaria con datetime-local
        
        # Agregar ayuda en los labels
        self.fields['start_time'].label = 'Fecha y Hora de Inicio'
        self.fields['end_time'].label = 'Fecha y Hora de Fin'
    def clean_start_time(self):
        """Validar hora de inicio."""
        start_time = self.cleaned_data.get('start_time')
        
        if start_time:
            # Para demostración, ser extremadamente permisivo con las fechas
            # Esto permitirá crear reservas incluso en el pasado reciente (hasta 1 hora atrás)
            now = timezone.now() - timedelta(hours=1)  # Permitir hasta 1 hora en el pasado para demos
            
            if start_time < now:
                current_time = timezone.now().strftime('%d/%m/%Y %H:%M')
                raise ValidationError(
                    f"Las reservas no pueden ser en el pasado lejano. "
                    f"Hora actual: {current_time}"
                )
            
            # No permitir reservas con más de 30 días de anticipación
            max_advance = timezone.now() + timedelta(days=30)
            if start_time > max_advance:
                raise ValidationError(
                    "No se pueden hacer reservas con más de 30 días de anticipación"
                )
        
        return start_time
    
    def clean_end_time(self):
        """Validar hora de fin."""
        end_time = self.cleaned_data.get('end_time')
        start_time = self.cleaned_data.get('start_time')
        
        if end_time and start_time:
            if end_time <= start_time:
                raise ValidationError(
                    "La hora de fin debe ser posterior a la hora de inicio"
                )
            # Validar duración
            duration = end_time - start_time
            if duration < timedelta(minutes=1): # Cambiado a 1 minuto para demostración
                raise ValidationError(
                    "La duración mínima de una reserva es 1 minuto"
                )
            
            if duration > timedelta(hours=8):
                raise ValidationError(
                    "La duración máxima de una reserva es 8 horas"
                )
        
        return end_time
    
    def clean_attendees_count(self):
        """Validar número de asistentes."""
        attendees_count = self.cleaned_data.get('attendees_count')
        room = self.cleaned_data.get('room')
        
        if attendees_count and room:
            if attendees_count > room.capacity:
                raise ValidationError(
                    f"El número de asistentes ({attendees_count}) excede "
                    f"la capacidad de la sala ({room.capacity})"
                )
        
        return attendees_count
    
    def clean(self):
        """Validación cruzada completa."""
        cleaned_data = super().clean()
        room = cleaned_data.get('room')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if room and start_time and end_time:
            # NUEVA: Validación de seguridad antes de otras validaciones
            if self.user:
                try:
                    from core.reservation_security import SecurityManager
                    
                    # Validar límites de seguridad
                    security_result = SecurityManager.validate_reservation_security(
                        user=self.user,
                        room=room,
                        start_time=start_time,
                        end_time=end_time
                    )
                    
                    if not security_result['allowed']:
                        # Crear mensaje detallado con todas las violaciones
                        violation_messages = [v['message'] for v in security_result['violations']]
                        raise ValidationError(
                            f"No se puede crear la reserva por límites de seguridad: " +
                            "; ".join(violation_messages)
                        )
                        
                    # Mostrar advertencias si existen (no bloquean la reserva)
                    if security_result['warnings']:
                        # Las advertencias se mostrarán en la vista
                        self._security_warnings = security_result['warnings']
                        
                except ImportError:
                    # Si el módulo de seguridad no está disponible, continuar sin validación
                    pass
                except Exception as e:
                    # Log del error pero no bloquear la reserva por errores del sistema de seguridad
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error en validación de seguridad de reservas: {e}")
            
            # Verificar horarios de operación de la sala
            start_date = start_time.date()
            end_date = end_time.date()
            
            # Verificar que la hora de inicio esté dentro del horario de operación
            if start_time.time() < room.opening_time or start_time.time() > room.closing_time:
                raise ValidationError(
                    f"La sala '{room.name}' opera de "
                    f"{room.opening_time.strftime('%H:%M')} a "
                    f"{room.closing_time.strftime('%H:%M')}"
                )
            
            # Verificar que la hora de fin esté dentro del horario de operación
            # Si la reserva termina el mismo día, verificar que no exceda el horario de cierre
            if start_date == end_date:
                if end_time.time() > room.closing_time:
                    raise ValidationError(
                        f"La sala '{room.name}' opera de "
                        f"{room.opening_time.strftime('%H:%M')} a "
                        f"{room.closing_time.strftime('%H:%M')}"
                    )
            else:
                # Si la reserva cruza medianoche, no debería ser permitida
                # ya que las salas no operan 24 horas
                raise ValidationError(
                    f"Las reservas no pueden extenderse más allá de medianoche. "
                    f"La sala '{room.name}' opera de "
                    f"{room.opening_time.strftime('%H:%M')} a "
                    f"{room.closing_time.strftime('%H:%M')}"
                )
            
            # Verificar disponibilidad de la sala
            overlapping_reservations = room.reservations.filter(
                status__in=['confirmed', 'in_progress'],
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            
            # Excluir la reserva actual si estamos editando
            if self.instance.pk:
                overlapping_reservations = overlapping_reservations.exclude(
                    pk=self.instance.pk
                )
            
            if overlapping_reservations.exists():
                conflicting_reservation = overlapping_reservations.first()
                raise ValidationError(
                    f"La sala no está disponible en el horario seleccionado. "
                    f"Conflicto con reserva existente: "
                    f"{conflicting_reservation.start_time.strftime('%d/%m/%Y %H:%M')} - "
                    f"{conflicting_reservation.end_time.strftime('%H:%M')}"
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        """Guardar reserva con usuario asignado."""
        reservation = super().save(commit=False)
        
        if self.user:
            reservation.user = self.user
        
        if commit:
            reservation.save()
        
        return reservation


class ReviewForm(forms.ModelForm):
    """
    Formulario para crear reseñas de salas.
    
    Permite a los usuarios calificar salas después de completar
    una reserva.
    """
    class Meta:
        model = Review
        fields = [
            'rating', 'cleanliness_rating', 'equipment_rating', 
            'comfort_rating', 'comment', 'comment_type'
        ]
        widgets = {
            'rating': forms.Select(
                choices=[(i, f"{i} estrella{'s' if i != 1 else ''}") for i in range(1, 6)],
                attrs={'class': 'form-select'}
            ),
            'cleanliness_rating': forms.Select(
                choices=[(i, f"{i} estrella{'s' if i != 1 else ''}") for i in range(1, 6)],
                attrs={'class': 'form-select'}
            ),
            'equipment_rating': forms.Select(
                choices=[(i, f"{i} estrella{'s' if i != 1 else ''}") for i in range(1, 6)],
                attrs={'class': 'form-select'}
            ),
            'comfort_rating': forms.Select(
                choices=[(i, f"{i} estrella{'s' if i != 1 else ''}") for i in range(1, 6)],
                attrs={'class': 'form-select'}
            ),
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Comparte tu experiencia con esta sala...',
                'class': 'form-control'
            }),
            'comment_type': forms.Select(attrs={'class': 'form-select'})
        }
        labels = {
            'rating': 'Calificación General',
            'cleanliness_rating': 'Limpieza',
            'equipment_rating': 'Equipamiento',
            'comfort_rating': 'Comodidad',
            'comment': 'Comentario',
            'comment_type': 'Tipo de Comentario'
        }
        help_texts = {
            'rating': 'Calificación general de tu experiencia',
            'cleanliness_rating': '¿Qué tan limpia estaba la sala?',
            'equipment_rating': '¿Cómo estuvo el equipamiento disponible?',
            'comfort_rating': '¿Qué tan cómoda fue la sala?',
            'comment': 'Comparte detalles específicos sobre tu experiencia (opcional)',
            'comment_type': 'Ayúdanos a categorizar tu comentario'
        }
    
    def __init__(self, *args, **kwargs):
        # Extraer la reserva si se pasa como parámetro
        self.reservation = kwargs.pop('reservation', None)
        super().__init__(*args, **kwargs)
        
        # Agregar clases CSS a todos los campos
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
    
    def save(self, commit=True):
        """Guardar la reseña asignando la reserva."""
        instance = super().save(commit=False)
        
        # Asignar la reserva si se proporcionó
        if self.reservation:
            instance.reservation = self.reservation
        
        if commit:
            instance.save()
        
        return instance


class RoomSearchForm(forms.Form):
    """
    Formulario para búsqueda y filtrado de salas.
    
    Permite filtrar salas por diversos criterios
    para facilitar la búsqueda de usuarios.
    """
    
    # Opciones para roles de usuario
    ROLE_CHOICES = [
        ('', 'Todas las salas'),
        ('estudiante', 'Solo salas para estudiantes'),
        ('profesor', 'Salas para profesores'),
        ('administrador', 'Todas las salas (admin)'),
        ('soporte', 'Salas de soporte técnico'),
    ]
      # Opciones para disponibilidad
    AVAILABILITY_CHOICES = [
        ('', 'Todas las salas'),
        ('available_now', 'Disponibles ahora'),
        ('available_today', 'Disponibles hoy'),
        ('available_custom', 'Disponibles en horario específico'),
    ]
    
    # Opciones para tipos de sala
    ROOM_TYPE_CHOICES = [
        ('', 'Todos los tipos'),
        ('aula', 'Aula'),
        ('sala_estudio', 'Sala de Estudio'),
        ('sala_individual', 'Sala Individual'),
        ('sala_reunion', 'Sala de Reuniones'),
        ('laboratorio', 'Laboratorio'),
        ('auditorio', 'Auditorio'),
    ]
    
    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar por nombre o ubicación...',
            'class': 'form-control'
        })    )
    
    min_capacity = forms.IntegerField(
        min_value=1,
        max_value=500,  # Límite razonable para capacidad máxima
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Capacidad mínima (1-500)',
            'class': 'form-control',
            'min': '1',
            'max': '500'
        })
    )
    
    # Nuevo: Filtro por rol de usuario
    user_role_filter = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Filtrar por acceso de rol'
    )
      # Filtro por disponibilidad
    availability_filter = forms.ChoiceField(
        choices=AVAILABILITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),        
        label='Filtrar por disponibilidad'
    )
    
    # Nuevo: Filtro por tipo de sala
    room_type_filter = forms.ChoiceField(
        choices=ROOM_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Tipo de sala'
    )
    
    available_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

    def clean(self):
        """Validación de búsqueda por disponibilidad."""
        cleaned_data = super().clean()
        available_date = cleaned_data.get('available_date')
        availability_filter = cleaned_data.get('availability_filter')
        min_capacity = cleaned_data.get('min_capacity')
        
        # Validación de capacidad
        if min_capacity and min_capacity > 500:
            raise ValidationError(
                "La capacidad máxima permitida es de 500 personas"
            )
        
        # Si se especifica búsqueda por horario específico, requiere fecha
        if availability_filter == 'available_custom':
            if not available_date:
                raise ValidationError(
                    "Para buscar por horario específico, debe especificar una fecha"
                )
        
        return cleaned_data
