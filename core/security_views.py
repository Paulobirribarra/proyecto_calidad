"""
Vistas para el dashboard de seguridad de reservas.

Proporciona información detallada sobre el uso del sistema
y estadísticas de seguridad para administradores.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta
import json

from core.reservation_security import ReservationSecurityRule, ReservationUsageLog, SecurityManager
from rooms.models import Reservation
from django.contrib.auth import get_user_model

User = get_user_model()


def is_admin_or_staff(user):
    """Verificar si el usuario es admin o staff."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@login_required
@user_passes_test(is_admin_or_staff)
def security_dashboard(request):
    """Dashboard principal de seguridad de reservas."""
    
    # Estadísticas generales
    now = timezone.now()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Logs recientes
    recent_logs = ReservationUsageLog.objects.filter(
        timestamp__gte=week_ago
    ).order_by('-timestamp')[:50]
    
    # Usuarios más activos
    active_users = ReservationUsageLog.objects.filter(
        timestamp__gte=week_ago,
        action='create'
    ).values('user__username').annotate(
        reservation_count=Count('id')
    ).order_by('-reservation_count')[:10]
    
    # Patrones sospechosos recientes
    suspicious_users = []
    for user in User.objects.filter(is_active=True):
        suspicions = SecurityManager.detect_suspicious_patterns(user)
        if suspicions:
            suspicious_users.append({
                'user': user,
                'suspicions': suspicions
            })
    
    # Violaciones por tipo
    violation_stats = ReservationUsageLog.objects.filter(
        timestamp__gte=week_ago,
        action='attempt_blocked'
    ).extra(
        select={'violation_type': "JSON_EXTRACT(additional_data, '$.violations[0]')"}
    ).values('violation_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Reglas de seguridad activas
    security_rules = ReservationSecurityRule.objects.filter(is_active=True)
    
    # Usuarios bloqueados actualmente
    blocked_users = []
    for user in User.objects.filter(is_active=True):
        is_blocked, blocked_until = SecurityManager.is_user_blocked(user)
        if is_blocked:
            blocked_users.append({
                'user': user,
                'blocked_until': blocked_until
            })
    
    context = {
        'recent_logs': recent_logs,
        'active_users': active_users,
        'suspicious_users': suspicious_users,
        'violation_stats': violation_stats,
        'security_rules': security_rules,
        'blocked_users': blocked_users,
        'stats': {
            'total_logs_week': recent_logs.count(),
            'blocked_attempts_week': ReservationUsageLog.objects.filter(
                timestamp__gte=week_ago,
                action='attempt_blocked'
            ).count(),
            'successful_reservations_week': ReservationUsageLog.objects.filter(
                timestamp__gte=week_ago,
                action='create'
            ).count(),
            'unique_users_week': ReservationUsageLog.objects.filter(
                timestamp__gte=week_ago
            ).values('user').distinct().count(),
        }
    }
    
    return render(request, 'admin/security_dashboard.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def security_stats_api(request):
    """API para obtener estadísticas de seguridad en formato JSON."""
    
    days = int(request.GET.get('days', 7))
    
    now = timezone.now()
    start_date = now - timedelta(days=days)
    
    # Datos por día
    daily_stats = []
    for i in range(days):
        day = start_date + timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_data = {
            'date': day.strftime('%Y-%m-%d'),
            'successful_reservations': ReservationUsageLog.objects.filter(
                timestamp__gte=day_start,
                timestamp__lt=day_end,
                action='create'
            ).count(),
            'blocked_attempts': ReservationUsageLog.objects.filter(
                timestamp__gte=day_start,
                timestamp__lt=day_end,
                action='attempt_blocked'
            ).count(),
            'warnings_sent': ReservationUsageLog.objects.filter(
                timestamp__gte=day_start,
                timestamp__lt=day_end,
                action='warning_sent'
            ).count(),
            'users_blocked': ReservationUsageLog.objects.filter(
                timestamp__gte=day_start,
                timestamp__lt=day_end,
                action='user_blocked'
            ).count(),
        }
        daily_stats.append(day_data)
    
    # Violaciones por tipo
    violation_types = ReservationUsageLog.objects.filter(
        timestamp__gte=start_date,
        action='attempt_blocked'
    ).values('additional_data').distinct()
    
    violation_counts = {}
    for log in violation_types:
        try:
            data = log['additional_data']
            if isinstance(data, str):
                data = json.loads(data)
            violations = data.get('violations', [])
            for violation in violations:
                violation_counts[violation] = violation_counts.get(violation, 0) + 1
        except:
            continue
    
    return JsonResponse({
        'daily_stats': daily_stats,
        'violation_types': violation_counts,
        'period_days': days
    })


@login_required
@user_passes_test(is_admin_or_staff)
def user_security_detail(request, user_id):
    """Detalle de seguridad para un usuario específico."""
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
    
    # Información de seguridad del usuario
    security_rules = SecurityManager.get_security_rules(user)
    is_blocked, blocked_until = SecurityManager.is_user_blocked(user)
    rate_allowed, violations, warnings = SecurityManager.check_rate_limits(user)
    suspicions = SecurityManager.detect_suspicious_patterns(user)
    
    # Historial reciente
    recent_logs = ReservationUsageLog.objects.filter(
        user=user,
        timestamp__gte=timezone.now() - timedelta(days=30)
    ).order_by('-timestamp')[:20]
    
    # Estadísticas del usuario
    now = timezone.now()
    user_stats = {
        'total_reservations': Reservation.objects.filter(user=user).count(),
        'active_reservations': Reservation.objects.filter(
            user=user,
            status__in=['confirmed', 'in_progress'],
            start_time__lte=now,
            end_time__gt=now
        ).count(),
        'reservations_this_week': Reservation.objects.filter(
            user=user,
            created_at__gte=now - timedelta(days=7)
        ).count(),
        'blocked_attempts_this_week': ReservationUsageLog.objects.filter(
            user=user,
            action='attempt_blocked',
            timestamp__gte=now - timedelta(days=7)
        ).count(),
    }
    
    context = {
        'target_user': user,
        'security_rules': security_rules,
        'is_blocked': is_blocked,
        'blocked_until': blocked_until,
        'rate_allowed': rate_allowed,
        'violations': violations,
        'warnings': warnings,
        'suspicions': suspicions,
        'recent_logs': recent_logs,
        'user_stats': user_stats,
    }
    
    return render(request, 'admin/user_security_detail.html', context)
