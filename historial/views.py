from historial.utils import (
    registrar_creacion,
    registrar_cambio_estado,
    registrar_cambio_prioridad,
    registrar_cambio_responsable,
    registrar_edicion,
    registrar_comentario,
)


# ── tarea_crear ──────────────────────────────
@login_required
@admin_o_manager
def tarea_crear(request):
    if request.method == 'POST':
        form = TareaForm(request.POST, user=request.user)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.creador = request.user
            tarea.save()
            registrar_creacion(tarea, request.user)  # ← NUEVO
            messages.success(request, f'✅ Tarea "{tarea.titulo}" creada.')
            return redirect('tarea_detalle', pk=tarea.pk)
    else:
        form = TareaForm(user=request.user)
    return render(request, 'tareas/form.html', {'form': form, 'titulo': 'Crear Tarea'})


# ── tarea_editar ─────────────────────────────
@login_required
def tarea_editar(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk)

    if not VerificarPermiso.puede_gestionar_tarea(request.user, tarea):
        messages.error(request, '❌ No tienes permiso.')
        return redirect('tarea_lista')

    if request.method == 'POST':
        # Guardar valores anteriores ANTES de editar
        prioridad_anterior   = tarea.prioridad
        responsable_anterior = tarea.responsable

        form = TareaForm(request.POST, instance=tarea, user=request.user)
        if form.is_valid():
            tarea_actualizada = form.save()

            # Registrar cambios específicos
            if prioridad_anterior != tarea_actualizada.prioridad:
                registrar_cambio_prioridad(
                    tarea_actualizada, request.user,
                    prioridad_anterior, tarea_actualizada.prioridad
                )
            if responsable_anterior != tarea_actualizada.responsable:
                registrar_cambio_responsable(
                    tarea_actualizada, request.user,
                    responsable_anterior, tarea_actualizada.responsable
                )

            registrar_edicion(tarea_actualizada, request.user)  # ← NUEVO
            messages.success(request, '✅ Tarea actualizada.')
            return redirect('tarea_detalle', pk=tarea.pk)
    else:
        form = TareaForm(instance=tarea, user=request.user)

    return render(request, 'tareas/form.html', {
        'form': form, 'titulo': 'Editar Tarea', 'tarea': tarea
    })


# ── tarea_cambiar_estado ─────────────────────
@login_required
def tarea_cambiar_estado(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk)

    if not VerificarPermiso.puede_gestionar_tarea(request.user, tarea):
        messages.error(request, '❌ No tienes permiso.')
        return redirect('tarea_detalle', pk=pk)

    if request.method == 'POST':
        nuevo_estado  = request.POST.get('estado')
        if nuevo_estado in dict(Tarea.ESTADOS):
            estado_anterior = tarea.estado      # ← Guardar antes
            tarea.estado    = nuevo_estado
            tarea.save()
            registrar_cambio_estado(            # ← NUEVO
                tarea, request.user,
                estado_anterior, nuevo_estado
            )
            messages.success(request, f'✅ Estado cambiado a: {tarea.get_estado_display()}')

    return redirect('tarea_detalle', pk=pk)


# ── tarea_detalle (comentarios) ──────────────
@login_required
def tarea_detalle(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk)

    if not VerificarPermiso.puede_ver_tarea(request.user, tarea):
        messages.error(request, '❌ No tienes acceso.')
        return redirect('tarea_lista')
    
    historial_cambios = HistorialTarea.objects.filter(tarea=tarea).order_by('-creado_en')

    comentarios = tarea.comentarios.all().order_by('creado_en')

    if request.method == 'POST':
        form_comentario = ComentarioForm(request.POST)
        if form_comentario.is_valid():
            comentario          = form_comentario.save(commit=False)
            comentario.tarea    = tarea
            comentario.usuario  = request.user
            comentario.save()
            registrar_comentario(tarea, request.user)  # ← NUEVO
            messages.success(request, '💬 Comentario agregado.')
            return redirect('tarea_detalle', pk=tarea.pk)
    else:
        form_comentario = ComentarioForm()

    context = {
        'tarea': tarea,
        'comentarios': comentarios,
        'form_comentario': form_comentario,
        'puede_editar': VerificarPermiso.puede_gestionar_tarea(request.user, tarea),
        'puede_eliminar': VerificarPermiso.puede_eliminar_tarea(request.user, tarea),
        'puede_cambiar_estado': VerificarPermiso.puede_gestionar_tarea(request.user, tarea),
        'estados': Tarea.ESTADOS,
        'historial':historial_cambios, 
    }
    return render(request, 'tareas/detalle.html', context)