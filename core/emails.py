# core/emails.py

"""
Sistema de notificaciones por email
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def enviar_email_base(asunto, destinatarios, template_html, contexto):
    """
    Función base para enviar emails HTML
    
    Args:
        asunto: Asunto del email
        destinatarios: Lista de emails destino
        template_html: Ruta del template HTML
        contexto: Diccionario con datos para el template
    """
    try:
        # Renderizar HTML
        html_content = render_to_string(template_html, contexto)
        
        # Versión texto plano (fallback)
        text_content = strip_tags(html_content)
        
        # Crear email
        email = EmailMultiAlternatives(
            subject=asunto,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=destinatarios
        )
        
        # Adjuntar versión HTML
        email.attach_alternative(html_content, "text/html")
        
        # Enviar
        email.send(fail_silently=False)
        
        return True
        
    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False


# ===== NOTIFICACIONES ESPECÍFICAS =====

def email_tarea_asignada(tarea, responsable):
    """
    Envía email cuando se asigna una tarea a alguien
    """
    asunto = f"Nueva tarea asignada: {tarea.titulo}"
    
    contexto = {
        'tarea': tarea,
        'responsable': responsable,
        'url_tarea': f"{settings.SITE_URL}/tareas/{tarea.pk}/" if hasattr(settings, 'SITE_URL') else f"http://127.0.0.1:8000/tareas/{tarea.pk}/",
    }
    
    return enviar_email_base(
        asunto=asunto,
        destinatarios=[responsable.email],
        template_html='emails/tarea_asignada.html',
        contexto=contexto
    )


def email_tarea_vencida(tarea):
    """
    Envía email cuando una tarea está vencida
    """
    if not tarea.responsable or not tarea.responsable.email:
        return False
    
    asunto = f"⚠️ Tarea vencida: {tarea.titulo}"
    
    contexto = {
        'tarea': tarea,
        'responsable': tarea.responsable,
        'url_tarea': f"{settings.SITE_URL}/tareas/{tarea.pk}/" if hasattr(settings, 'SITE_URL') else f"http://127.0.0.1:8000/tareas/{tarea.pk}/",
    }
    
    return enviar_email_base(
        asunto=asunto,
        destinatarios=[tarea.responsable.email],
        template_html='emails/tarea_vencida.html',
        contexto=contexto
    )


def email_tarea_completada(tarea, completada_por):
    """
    Notifica al creador cuando se completa su tarea
    """
    if not tarea.creador or not tarea.creador.email:
        return False
    
    # No enviar si el creador es quien la completó
    if tarea.creador == completada_por:
        return False
    
    asunto = f"✅ Tarea completada: {tarea.titulo}"
    
    contexto = {
        'tarea': tarea,
        'completada_por': completada_por,
        'creador': tarea.creador,
        'url_tarea': f"{settings.SITE_URL}/tareas/{tarea.pk}/" if hasattr(settings, 'SITE_URL') else f"http://127.0.0.1:8000/tareas/{tarea.pk}/",
    }
    
    return enviar_email_base(
        asunto=asunto,
        destinatarios=[tarea.creador.email],
        template_html='emails/tarea_completada.html',
        contexto=contexto
    )


def email_comentario_nuevo(comentario, usuarios_notificar):
    """
    Notifica sobre un nuevo comentario en una tarea
    
    Args:
        comentario: Objeto Comentario
        usuarios_notificar: Lista de usuarios a notificar
    """
    emails_destino = [u.email for u in usuarios_notificar if u.email]
    
    if not emails_destino:
        return False
    
    asunto = f"💬 Nuevo comentario en: {comentario.tarea.titulo}"
    
    contexto = {
        'comentario': comentario,
        'tarea': comentario.tarea,
        'url_tarea': f"{settings.SITE_URL}/tareas/{comentario.tarea.pk}/" if hasattr(settings, 'SITE_URL') else f"http://127.0.0.1:8000/tareas/{comentario.tarea.pk}/",
    }
    
    return enviar_email_base(
        asunto=asunto,
        destinatarios=emails_destino,
        template_html='emails/comentario_nuevo.html',
        contexto=contexto
    )


def email_cambio_prioridad(tarea, prioridad_anterior, prioridad_nueva, cambiado_por):
    """
    Notifica cuando cambia la prioridad de una tarea a Urgente
    """
    # Solo enviar si cambió a urgente
    if prioridad_nueva != 'urgente':
        return False
    
    if not tarea.responsable or not tarea.responsable.email:
        return False
    
    asunto = f"🔴 Prioridad cambiada a URGENTE: {tarea.titulo}"
    
    contexto = {
        'tarea': tarea,
        'prioridad_anterior': prioridad_anterior,
        'prioridad_nueva': prioridad_nueva,
        'cambiado_por': cambiado_por,
        'url_tarea': f"{settings.SITE_URL}/tareas/{tarea.pk}/" if hasattr(settings, 'SITE_URL') else f"http://127.0.0.1:8000/tareas/{tarea.pk}/",
    }
    
    return enviar_email_base(
        asunto=asunto,
        destinatarios=[tarea.responsable.email],
        template_html='emails/prioridad_urgente.html',
        contexto=contexto
    )