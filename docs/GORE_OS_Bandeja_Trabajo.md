# Bandeja de trabajo GORE_OS

El incremento vigente concentra la entrada del funcionario en los pendientes de
su ámbito: qué debe atender, quién es el responsable registrado, en qué estado
está y cuál es la siguiente acción disponible. Continúa el journey J1 y los
principios P1/P2 de `GORE_OS_User_Journeys_v3.0.md`.

## Recorrido

1. Iniciar sesión con una cuenta activa y un rol registrado en PostgreSQL.
2. Abrir `/dashboard`: la bandeja muestra pendientes priorizados, con búsqueda,
   tipo y filtro de asignación personal. La navegación fija esta entrada para
   las poblaciones operativa y DGI.
3. Abrir un compromiso mediante `/compromisos?id=<uuid>`. La asignación del
   compromiso gobierna este acceso personal, aunque la IPR tenga otro encargado.
4. Ejecutar la acción que devuelve `allowed_actions`. Completar pasa a
   `COMPLETADO`; deja la bandeja del ejecutor y aparece para la verificación del
   supervisor habilitado. Devolver exige motivo y retorna a `EN_PROGRESO`.
5. Volver a la bandeja o actualizarla para consultar el estado persistido.

Un usuario de alcance personal no puede sustituir su responsable con un filtro,
abrir o editar un compromiso ajeno. Un rol de solo lectura conserva la lectura
permitida; la asignación por sí sola no le concede escritura. La API verifica
la identidad y el rol desde la base, además de los controles de interfaz.

## Autoridad y fuentes

`core.operational_commitment` sigue siendo la autoridad del compromiso.
`ref.category.valid_transitions`, `trg_commitment_state_transition` y
`trg_commitment_history` validan y registran las transiciones. La API usa SQL
parametrizado. `api/app/core/commitments.py` reúne las reglas existentes que
resuelven las acciones del listado, detalle y bandeja; no crea otra tabla de
tareas ni un motor de workflow.

El feed `/api/dashboard/action-items` consulta las nueve fuentes existentes:
compromisos, alertas, decisiones AR, escalamientos, incumplimientos SLA, riesgos,
firmas, rendiciones e IPR que requieren atención. Conserva las restricciones de
lectura del dominio. Cuando el modelo no registra un responsable individual,
la interfaz declara esa ausencia. El estado y su glosa proceden de la categoría
persistida; “Sin resolver” deriva del filtro de alertas sin `resolved_at`.

La bandeja personal de compromisos cubre todos sus pendientes, paginados en la
interfaz. Las demás fuentes conservan cortes de atención de 5, 10 o 15 elementos;
el feed y la UI declaran cuando se alcanza ese corte. Los plazos de atención
existentes no se convierten en nuevas obligaciones legales.

## Herramientas y recuperación

Los panoramas, cockpits DGI, indicadores, formulación, equipo y revisión jurídica
se mantienen en `/panorama`. IPR, procesos, presupuesto, convenios, actos,
servicios y las demás herramientas siguen sus rutas y permisos existentes.
Los procesos de mejora no se convierten en tareas personales sin un contrato de
asignación y acción aplicable.

`/mis-compromisos` redirige a `/compromisos?mine=true`; `/mi-division` redirige
a `/panorama`. Se retiraron `AttentionStrip`, `ModuleMyWork`, el dashboard
operativo legacy, su desglose ejecutivo y `ModuleDgiTeam`, que carecía de
consumidor. La función de atención tiene una sola representación en la bandeja.
Las versiones anteriores son recuperables desde el historial Git anterior a
este incremento, con base `b8540f67`, y el checkpoint de saneamiento del operador.

## Verificación y consumo

La regresión está en `api/tests/test_work_inbox.py` y utiliza el circuito existente
de integración contra PostgreSQL real. Debe comprobarse el recorrido observable
con identidades y datos ficticios, además de las suites de compromisos, permisos
y dashboard, lint y build del frontend.

Un despliegue consume una release identificada por SHA, con código e interfaz
construidos desde ese mismo candidato. La API se ejecuta sin `--reload` y la web
desde su build; ninguno depende del checkout de desarrollo. Se conserva la base
vigente y la configuración privada externa. La evidencia técnica de este
incremento no acredita adopción institucional ni disponibilidad de un runtime.
