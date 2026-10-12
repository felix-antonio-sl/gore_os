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
| IPR sin movimiento | `/ipr/<uuid>`; consulta del expediente y trabajo relacionado | Ámbito personal/divisional/institucional vigente; IPR de sólo lectura, sin creación, edición o transición |

Los compromisos personales se consultan completos y paginados. Otras fuentes tienen
cortes de atención de 5, 10 o 15 elementos; feed y UI declaran cuándo se alcanza el
corte. Los lectores de cada fuente permiten continuar la consulta paginada. Cuando
no hay responsable individual registrado, la UI lo declara. Los plazos actuales son
criterios de atención del modelo, no obligaciones legales nuevas.

## Expediente y acciones relacionadas

Por la decisión de alcance de Félix del 12 de octubre de 2026, el expediente IPR
conserva consulta de estado/fase y responsables registrados. Sus secciones de trabajo
abren compromisos, problemas, alertas, convenios y rendiciones mediante la identidad
exacta del objeto. Las listas relacionadas están paginadas y distinguen fallo de carga
de ausencia de registros. Los permisos de cada acción siguen perteneciendo a su API.

Antecedentes ofrece mecanismo y atributos registrados, historial completo, CDP,
resoluciones, avances, organizaciones/territorio, hitos, evaluaciones, admisibilidad,
certificación, parentesco, modificaciones, cierre y evaluación posterior. No presenta
capturas o instrucciones de siguiente fase. `/api/ipr` sólo registra métodos GET;
la lectura de CDP verifica el mismo acceso al expediente que los demás antecedentes.
El estado y la fase mostrados son los almacenados, sin deducir un siguiente actor.

Las acciones de compromisos, problemas, alertas, convenios y rendiciones no cambian
el estado, la fase ni la asignación del IPR. Conservan sus propios historiales,
transiciones y controles de autoridad. Los umbrales financieros que consumen actos y
convenios siguen configurables. Se retiró la administración exclusiva de transición
IPR, SNI, vías/fondos de financiamiento, admisibilidad y programas presupuestarios.
Sus tablas y datos permanecen como antecedentes recuperables.

## Capacidades archivadas y recuperación

Se retiraron páginas, APIs exclusivas, componentes, DTO y dependencias sin consumidores
de panoramas/cockpits, tablero de iniciativas/DMAIC, cuellos de botella, informes,
comité TD, reuniones/calendario, exploradores generales de datos, vistas autónomas de
cartera/formulación, equipo y captura de bugs. La bandeja tiene una representación
activa. También se retiraron creación/transiciones/capturas de IPR y los módulos
autónomos CORE y presupuesto/CDP. Las entidades, tablas, categorías y datos de
dominio se conservan; el retiro de
una interfaz no elimina un expediente ni una fuente histórica.

`/mis-compromisos` redirige a `/compromisos?mine=true`; `/mi-division` a la bandeja.
`/datos?dominio=rendiciones` conserva el enlace de rendición y los filtros al redirigir;
los demás exploradores anteriores llevan a la bandeja. Los enlaces antiguos de un
servicio redirigen a sus solicitudes. El código retirado se recupera desde Git en
`6c387ed0aad8721f2b22202beb08f228e2235fe6`, además del checkpoint privado verificado
del operador. El ciclo IPR/CORE/CDP anterior a este último recorte se recupera
en `92d13a9e9524ccebdf59c676d6686862cd1aff04`. El [índice de archivo](archive/README.md) describe la función histórica.

## Verificación y consumo

`test_inbox_journeys` comprueba con PostgreSQL real identidad independiente de alertas
con texto igual, scope dueño/ajeno, plazos SLA antes/en/después del límite y con contratos
de productos distintos, firma canónica y lectura acotada de procesos. Las suites
conservadas cubren la consulta y permisos del expediente, las restricciones de los
escritores retirados y las acciones relacionadas. `test_ipr_consultation` comprueba
además que esas cinco acciones preservan la fase/asignación IPR y que los antecedentes
registrados siguen accesibles. El recorrido observable usa
identidades y expedientes ficticios en una base aislada; no usa cuentas o datos reales.

Una entrega identifica un SHA y construye API/web desde ese mismo candidato. La
configuración privada y base vigente permanecen fuera de la fuente pública. Las pruebas
no acreditan adopción o ratificación institucional. El despliegue y recuperación del
runtime se comprueban por separado siguiendo [la receta](GORE_OS_Despliegue.md).
