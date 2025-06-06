from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Room, Reservation, Review


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """Configuración del admin para Room."""
    
    list_display = (
        'name', 
        'capacity', 
        'location', 
        'is_active',
        'average_rating_display',
        'total_reservations',
        'hourly_rate'    )
    
    list_filter = (
        'is_active', 
        'capacity', 
        'created_at',
        'hourly_rate',
        'room_type'  # Añadimos filtro por tipo de sala
    )
    
    search_fields = ('name', 'location', 'description')
    list_editable = ('is_active', 'hourly_rate')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'capacity', 'location')
        }),
        ('Configuración', {
            'fields': ('is_active', 'hourly_rate', 'opening_time', 'closing_time')
        }),
        ('Equipamiento', {
            'fields': ('equipment',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        """Asignar el usuario creador si está autenticado."""
        if not change and request.user.is_authenticated:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    def average_rating_display(self, obj):
        """Mostrar calificación promedio con estrellas."""
        try:
            rating = obj.average_rating
            if rating is not None and rating > 0:
                # Formatear primero el valor de rating para evitar usar .1f con SafeString
                rating_formatted = "{:.1f}".format(rating)
                stars = '★' * int(rating) + '☆' * (5 - int(rating))
                return format_html(
                    '<span title="{0} estrellas">{1} ({2})</span>',
                    rating_formatted, stars, rating_formatted
                )
            return "Sin calificaciones"
        except (AttributeError, TypeError):
            return "Sin calificaciones"
    average_rating_display.short_description = "Calificación promedio"
    
    def total_reservations(self, obj):
        """Mostrar total de reservas con enlace al listado."""
        try:
            count = obj.reservations.count()
            if count > 0:
                url = reverse('admin:rooms_reservation_changelist')
                return format_html(
                    '<a href="{0}?room__id__exact={1}">{2} reservas</a>',
                    url, obj.id, count
                )
            return "0 reservas"
        except Exception:
            return "0 reservas"
    total_reservations.short_description = "Total reservas"
    
    def get_queryset(self, request):
        """Optimizar consultas."""
        return super().get_queryset(request).select_related(
            'created_by'
        ).prefetch_related('reservations')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """Configuración del admin para Reservation."""
    
    list_display = (
        'room',
        'user', 
        'start_time',
        'duration_display',
        'status',
        'attendees_count',
        'has_review'
    )
    
    list_filter = (
        'status',
        'room',
        'start_time',
        'created_at'
    )
    
    search_fields = (
        'room__name',
        'user__username',
        'user__email',
        'purpose'
    )
    
    list_editable = ('status',)
    date_hierarchy = 'start_time'
    
    fieldsets = (
        ('Reserva', {
            'fields': ('room', 'user', 'start_time', 'end_time', 'status')
        }),
        ('Detalles', {
            'fields': ('purpose', 'attendees_count', 'notes')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    def duration_display(self, obj):
        """Mostrar duración de la reserva."""
        try:
            hours = obj.duration_hours_rounded
            if hours is None:
                return "N/A"
            if hours >= 1:
                return "{} horas".format(hours)
            else:
                minutes = int(hours * 60)
                return "{} min".format(minutes)
        except (AttributeError, TypeError):
            return "N/A"
    duration_display.short_description = "Duración"
    
    def has_review(self, obj):
        """Indicar si tiene reseña."""
        try:
            if obj.review.exists():
                return format_html(
                    '<span style="color: green;">★ {0}</span>',
                    obj.review.first().rating
                )
            elif hasattr(obj, 'can_be_reviewed') and obj.can_be_reviewed():
                return format_html(
                    '<span style="color: orange;">Pendiente</span>'
                )
            return format_html('<span style="color: gray;">N/A</span>')
        except Exception:
            return format_html('<span style="color: gray;">N/A</span>')
    has_review.short_description = "Reseña"
    
    def get_queryset(self, request):
        """Optimizar consultas."""
        return super().get_queryset(request).select_related(
            'room', 'user'
        ).prefetch_related('review')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Configuración del admin para Review."""
    
    list_display = (
        'reservation',
        'rating_display',
        'specific_ratings_display',
        'comment_type_display',
        'created_at'
    )
    
    list_filter = (
        'rating',
        'cleanliness_rating',
        'equipment_rating',
        'comfort_rating',
        'comment_type',
        'created_at'
    )
    
    search_fields = (
        'reservation__room__name',
        'reservation__user__username',
        'comment'
    )
    
    readonly_fields = ('reservation', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Reserva', {
            'fields': ('reservation',)
        }),
        ('Calificaciones', {
            'fields': (
                'rating',
                'cleanliness_rating',
                'equipment_rating',
                'comfort_rating'
            )
        }),
        ('Comentario', {
            'fields': ('comment', 'comment_type')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rating_display(self, obj):
        """Mostrar calificación general con estrellas."""
        try:
            stars = '★' * obj.rating + '☆' * (5 - obj.rating)
            return format_html(
                '<span title="{0} estrellas">{1}</span>',
                obj.rating, stars
            )
        except (AttributeError, TypeError):
            return "N/A"
    rating_display.short_description = "Calificación general"
    
    def specific_ratings_display(self, obj):
        """Mostrar calificaciones específicas."""
        try:
            cleanliness = obj.cleanliness_rating if obj.cleanliness_rating is not None else "N/A"
            equipment = obj.equipment_rating if obj.equipment_rating is not None else "N/A"
            comfort = obj.comfort_rating if obj.comfort_rating is not None else "N/A"
            return format_html(
                'L: {0} | E: {1} | C: {2}',
                cleanliness, equipment, comfort
            )
        except (AttributeError, TypeError):
            return "N/A"
    specific_ratings_display.short_description = "Limpieza/Equipo/Comodidad"
    
    def comment_type_display(self, obj):
        """Mostrar tipo de comentario con color."""
        colors = {
            'positive': '#28a745',
            'suggestion': '#007bff', 
            'problem': '#dc3545',
            'neutral': '#6c757d'
        }
        icons = {
            'positive': '👍',
            'suggestion': '💡',
            'problem': '⚠️',
            'neutral': '💬'
        }
        try:
            color = colors.get(obj.comment_type, '#6c757d')
            icon = icons.get(obj.comment_type, '💬')
            return format_html(
                '<span style="color: {0};">{1} {2}</span>',
                color, icon, obj.get_comment_type_display()
            )
        except (AttributeError, TypeError):
            return "N/A"
    comment_type_display.short_description = "Tipo de comentario"
    
    def get_queryset(self, request):
        """Optimizar consultas."""
        return super().get_queryset(request).select_related(
            'reservation__room', 'reservation__user'
        )