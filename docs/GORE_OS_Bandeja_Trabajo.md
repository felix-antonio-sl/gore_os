# Bandeja de trabajo GORE_OS

La entrada del funcionario es `/dashboard`: pendientes de su ámbito, responsable,
estado y siguiente acción disponible. Continúa J1 y los principios P1/P2 de
[GORE_OS_User_Journeys_v3.0.md](GORE_OS_User_Journeys_v3.0.md). El producto concentra
la bandeja transversal, sus detalles/acciones y la administración necesaria para
identidades, permisos y categorías. Las historias y modelos conservan el dominio;
los snapshots de superficies anteriores no definen el alcance activo.

## Recorrido y autoridad

1. Iniciar sesión con una cuenta activa y un rol registrado en PostgreSQL.
2. Consultar pendientes priorizados por temporalidad y gravedad; filtrar por tipo,
   buscar texto o limitar la asignación a uno mismo.
3. Abrir el enlace del objeto concreto y leer su contexto antes de actuar.
4. Ejecutar sólo las acciones que la API devuelve para ese usuario y estado.
5. Volver a la bandeja y comprobar el estado persistido.

La base es autoridad de las categorías, transiciones e historial. Se mantiene SQL
parametrizado, sin ORM ni otra tabla de tareas. El ámbito de atención reutiliza las
reglas de lectura de compromisos, alertas y riesgos; la atención no concede permisos
adicionales de escritura. Los endpoints verifican la identidad actual desde la DB.

| Fuente de atención | Lector/acción conservada | Autoridad y límite |
|---|---|---|
| Compromiso | `/compromisos?id=<uuid>`; completar, devolver con motivo y verificar | `allowed_actions`, asignación personal y supervisor autorizado; triggers de transición/historial |
| Alerta | `/alertas?id=<uuid>`; atender y consultar el sujeto | Identidad `core.alert.id`; mismo scope de listado y atención; atender registra fecha y no equivale a resolver |
| Decisión AR | `/coordinacion?id=<uuid>`; responsable y estado | Roles DGI/ejecutivos leen; JEFE_DGI y ESP_CONTROL_GESTION editan; destinos de categoría DB |
| Escalamiento | `/escalamiento/<uuid>`; contexto, gestión y resolución | Edición/destinos devueltos por API; FSM DB; roles lectores mantienen sólo consulta |
| Solicitud SLA | `/servicios/solicitudes/<uuid>`; estado, asignación y feedback | DGI lee institucionalmente; los demás sólo solicitudes propias. Plazo canónico `dgi_service.sla_days`, sin plazo si NULL; comparación fraccional de días igual al lector |
| Riesgo | `/riesgos/<uuid>`; mitigación y estado | DGI/admin editan; personas/jefaturas leen riesgos de sus IPR/división. Procesos relacionados tienen lector acotado, sin motor de mejora |
| Firma | `/actos?id=<uuid>` o `/convenios?id=<uuid>`; transición autorizada | Categoría persistida; API comprueba umbral de monto y bloquea destinos imposibles; historial y contexto IPR preservados |
| Rendición | `/rendiciones?id=<uuid>`; revisión SISREC | Destinos de categoría DB filtrados por roles existentes; captura, fases, observaciones e historial conservados |
| IPR sin movimiento | `/ipr/<uuid>`; contexto y ciclo vigente | Asignación/división; se conserva el ciclo completo IPR/CORE/CDP mientras se decide si el alcance IPR será sólo consultivo |

Los compromisos personales se consultan completos y paginados. Otras fuentes tienen
cortes de atención de 5, 10 o 15 elementos; feed y UI declaran cuándo se alcanza el
corte. Los lectores de cada fuente permiten continuar la consulta paginada. Cuando
no hay responsable individual registrado, la UI lo declara. Los plazos actuales son
criterios de atención del modelo, no obligaciones legales nuevas.

## Capturas y gates que permanecen

La reducción de panoramas conserva el ciclo contextual IPR original hasta la decisión
sobre consulta vs transición completa. No se ofrece una transición cuya captura haya
sido retirada. Las reglas de régimen y gates permanecen en DB/API y su UI contextual.

| Gate/condición | Captura o acción conservada | Regresión pertinente |
|---|---|---|
| Admisibilidad y evidencias | Pestaña contextual de admisibilidad y documentos IPR | `test_admissibility`, `test_ipr_readiness` |
| Resultado de evaluación según régimen | Asignaciones/resultados en evaluaciones IPR | `test_polyswitch`, `test_track_enforcement`, `test_ipr_bifurcation` |
| Financiamiento/CDP y aprobación CORE | Presupuesto, CDP y sesiones/acuerdos CORE originales | `test_presupuesto`, `test_core_sessions`, `test_ciclo24` |
| Formalización/ejecución y cambios | Contrato contextual, avances, modificaciones e ITO | `test_ipr_children`, `test_modifications`, `test_lifecycle_slas` |
| Cierre técnico/financiero | Captura y aprobación de cierre IPR | `test_closure`, `test_ipr_lifecycle` |
| Verificación de compromiso | Completar → supervisor devolver con motivo/verificar | `test_work_inbox`; recorrido con usuario responsable, supervisor y lector |
| Firma según monto y estado | Detalle de acto/convenio con acciones y bloqueo explicado | `test_thresholds`, `test_convenios`, `test_actos`, `test_inbox_journeys` |
| Revisión de rendición | Captura contextual, observación y transición autorizada | `test_rendiciones`, `test_sisrec`, `test_sisrec_8phase`, `test_dgi_data` |

## Capacidades archivadas y recuperación

Se retiraron páginas, APIs exclusivas, componentes, DTO y dependencias sin consumidores
de panoramas/cockpits, tablero de iniciativas/DMAIC, cuellos de botella, informes,
comité TD, reuniones/calendario, exploradores generales de datos, vistas autónomas de
cartera/formulación, equipo y captura de bugs. La bandeja tiene una representación
activa. Las entidades, tablas, categorías y datos de dominio se conservan; el retiro de
una interfaz no elimina un expediente ni una fuente histórica.

`/mis-compromisos` redirige a `/compromisos?mine=true`; `/mi-division` a la bandeja.
`/datos?dominio=rendiciones` conserva el enlace de rendición y los filtros al redirigir;
los demás exploradores anteriores llevan a la bandeja. Los enlaces antiguos de un
servicio redirigen a sus solicitudes. El código retirado se recupera desde Git en
`6c387ed0aad8721f2b22202beb08f228e2235fe6`, además del checkpoint privado verificado
del operador. El [índice de archivo](archive/README.md) describe la función histórica.

## Verificación y consumo

`test_inbox_journeys` comprueba con PostgreSQL real identidad independiente de alertas
con texto igual, scope dueño/ajeno, plazos SLA antes/en/después del límite y con contratos
de productos distintos, firma canónica y lectura acotada de procesos. Las suites
conservadas cubren los gates y permisos del ciclo IPR. El recorrido observable usa
identidades y expedientes ficticios en una base aislada; no usa cuentas o datos reales.

Una entrega identifica un SHA y construye API/web desde ese mismo candidato. La
configuración privada y base vigente permanecen fuera de la fuente pública. Las pruebas
no acreditan adopción o ratificación institucional. El despliegue y recuperación del
runtime se comprueban por separado siguiendo [la receta](GORE_OS_Despliegue.md).
