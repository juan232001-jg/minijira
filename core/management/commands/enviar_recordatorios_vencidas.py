from django.core.management.base import BaseCommand
from django.utils import timezone
from tareas.models import Tarea
from core.emails import email_tarea_vencida


class Command(BaseCommand):
    help = 'Envía recordatorios de tareas vencidas'

    def handle(self, *args, **kwargs):
        """Busca tareas vencidas y envía emails"""
        
        hoy = timezone.now().date()
        
        # Buscar tareas vencidas no completadas
        tareas_vencidas = Tarea.objects.filter(
            fecha_vencimiento__lt=hoy,
            estado__in=['pendiente', 'en_progreso', 'en_revision']
        ).select_related('responsable', 'proyecto')
        
        contador = 0
        
        for tarea in tareas_vencidas:
            if tarea.responsable and tarea.responsable.email:
                try:
                    email_tarea_vencida(tarea)
                    contador += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Email enviado: {tarea.titulo} → {tarea.responsable.email}'
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'❌ Error enviando email para "{tarea.titulo}": {e}'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Proceso completado: {contador} emails enviados'
            )
        )