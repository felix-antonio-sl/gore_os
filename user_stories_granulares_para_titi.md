# 📋 User Stories Granulares — Sistema de Gestión de Crisis IPR

> **Formato**: Como [ROL], quiero [ACCIÓN], para [BENEFICIO].

---

## 🔴 ROL: ADMINISTRADOR REGIONAL

### Dashboard y Visibilidad

| ID         | User Story                                                                                                                                                     |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **AR-01a** | Como **Administrador Regional**, quiero ver el número total de IPR activas en un resumen ejecutivo, para tener visibilidad inmediata del tamaño de la cartera. |
| **AR-01b** | Como **Administrador Regional**, quiero ver cuántas IPR tienen problemas abiertos, para priorizar mi atención en los casos críticos.                           |
| **AR-01c** | Como **Administrador Regional**, quiero ver el conteo de compromisos vencidos del día, para identificar incumplimientos de manera proactiva.                   |
| **AR-01d** | Como **Administrador Regional**, quiero ver alertas críticas destacadas en el dashboard, para actuar de inmediato ante situaciones urgentes.                   |

### Nudos Críticos

| ID         | User Story                                                                                                                                                |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **AR-02a** | Como **Administrador Regional**, quiero ver una lista filtrada de proyectos con nivel de alerta "CRÍTICO", para enfocar recursos en los casos más graves. |
| **AR-02b** | Como **Administrador Regional**, quiero ver el detalle del problema asociado a cada nudo crítico, para entender la naturaleza del bloqueo.                |
| **AR-02c** | Como **Administrador Regional**, quiero ver el responsable asignado a cada IPR crítica, para saber a quién convocar.                                      |
| **AR-02d** | Como **Administrador Regional**, quiero ver los días de antigüedad de cada problema crítico, para priorizar los más urgentes.                             |

### Preparación de Reuniones

| ID         | User Story                                                                                                                              |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **AR-03a** | Como **Administrador Regional**, quiero ver una agenda sugerida basada en alertas activas, para llegar preparado a la reunión semanal.  |
| **AR-03b** | Como **Administrador Regional**, quiero ver los compromisos vencidos agrupados por división, para estructurar la discusión por área.    |
| **AR-03c** | Como **Administrador Regional**, quiero ver los compromisos completados pendientes de verificación, para validarlos durante la reunión. |

### Conducción de Reuniones

| ID         | User Story                                                                                                                                            |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **AR-04a** | Como **Administrador Regional**, quiero abrir la ficha completa de una IPR durante la reunión, para revisar su estado en detalle.                     |
| **AR-04b** | Como **Administrador Regional**, quiero ver el historial de compromisos de una IPR, para entender el contexto de la gestión.                          |
| **AR-04c** | Como **Administrador Regional**, quiero crear un nuevo compromiso asignado a un responsable con fecha límite, para formalizar acuerdos de la reunión. |
| **AR-04d** | Como **Administrador Regional**, quiero vincular un compromiso a un problema existente, para mantener trazabilidad.                                   |
| **AR-04e** | Como **Administrador Regional**, quiero vincular un compromiso a una cuota específica, para precisar el alcance financiero.                           |

### Verificación de Compromisos

| ID         | User Story                                                                                                                                    |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **AR-05a** | Como **Administrador Regional**, quiero ver la lista de compromisos en estado "Completado" pendientes de verificación, para revisarlos.       |
| **AR-05b** | Como **Administrador Regional**, quiero leer el comentario de cierre del responsable, para evaluar si el compromiso se cumplió correctamente. |
| **AR-05c** | Como **Administrador Regional**, quiero marcar un compromiso como "Verificado", para cerrar formalmente el ciclo.                             |
| **AR-05d** | Como **Administrador Regional**, quiero rechazar un compromiso y devolverlo a "Pendiente" con un comentario, para solicitar correcciones.     |

### Entrevistas con Responsables

| ID         | User Story                                                                                                                                                                    |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **AR-06a** | Como **Administrador Regional**, quiero ver todos los compromisos vencidos de un encargado específico, para preparar la entrevista.                                           |
| **AR-06b** | Como **Administrador Regional**, quiero registrar un nuevo problema detectado durante la entrevista, para documentar hallazgos.                                               |
| **AR-06c** | Como **Administrador Regional**, quiero seleccionar el tipo de problema (Técnico, Financiero, Administrativo, Legal, Coordinación, Externo), para clasificarlo correctamente. |
| **AR-06d** | Como **Administrador Regional**, quiero especificar el impacto del problema (Bloquea pago, Retrasa obra, etc.), para priorizar su resolución.                                 |

### Informes Ejecutivos

| ID         | User Story                                                                                                                           |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **AR-07a** | Como **Administrador Regional**, quiero generar un resumen semanal con métricas de cumplimiento, para informar al Gobernador.        |
| **AR-07b** | Como **Administrador Regional**, quiero ver la tasa de compromisos cumplidos vs vencidos, para evaluar el desempeño global.          |
| **AR-07c** | Como **Administrador Regional**, quiero exportar el resumen ejecutivo a PDF, para enviarlo por correo.                               |
| **AR-07d** | Como **Administrador Regional**, quiero ver la evolución de problemas resueltos vs nuevos en la semana, para identificar tendencias. |

### Comparación por División

| ID         | User Story                                                                                                                                      |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **AR-08a** | Como **Administrador Regional**, quiero ver el ranking de divisiones por tasa de cumplimiento de compromisos, para identificar áreas de mejora. |
| **AR-08b** | Como **Administrador Regional**, quiero comparar el número de problemas abiertos por división, para detectar patrones organizacionales.         |
| **AR-08c** | Como **Administrador Regional**, quiero ver el tiempo promedio de resolución de problemas por división, para evaluar eficiencia.                |

---

## 🟠 ROL: JEFE DE DIVISIÓN

### Resumen de División

| ID         | User Story                                                                                                                 |
| ---------- | -------------------------------------------------------------------------------------------------------------------------- |
| **JD-01a** | Como **Jefe de División**, quiero ver el total de IPR asignadas a mi división, para conocer mi alcance de responsabilidad. |
| **JD-01b** | Como **Jefe de División**, quiero ver cuántas IPR de mi división tienen problemas abiertos, para priorizar intervenciones. |
| **JD-01c** | Como **Jefe de División**, quiero ver el total de compromisos pendientes de mi equipo, para organizar seguimiento.         |
| **JD-01d** | Como **Jefe de División**, quiero ver cuántos compromisos de mi división están vencidos, para tomar acciones correctivas.  |

### Estado del Equipo

| ID         | User Story                                                                                                                                   |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **JD-02a** | Como **Jefe de División**, quiero ver la lista de encargados de mi división con sus métricas de compromisos, para evaluar cargas de trabajo. |
| **JD-02b** | Como **Jefe de División**, quiero ver los compromisos pendientes de cada encargado, para identificar cuellos de botella.                     |
| **JD-02c** | Como **Jefe de División**, quiero ver indicadores visuales (⚠️, ✅) por encargado según su estado de compromisos, para una lectura rápida.     |

### Compromisos Vencidos

| ID         | User Story                                                                                                         |
| ---------- | ------------------------------------------------------------------------------------------------------------------ |
| **JD-03a** | Como **Jefe de División**, quiero filtrar compromisos vencidos de mi división, para listar los atrasos.            |
| **JD-03b** | Como **Jefe de División**, quiero ver los días de vencimiento de cada compromiso, para priorizar los más antiguos. |
| **JD-03c** | Como **Jefe de División**, quiero ver la IPR asociada a cada compromiso vencido, para entender el contexto.        |

### Asignación de Compromisos

| ID         | User Story                                                                                                                         |
| ---------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **JD-04a** | Como **Jefe de División**, quiero crear un compromiso y asignarlo a un encargado de mi división, para distribuir tareas.           |
| **JD-04b** | Como **Jefe de División**, quiero seleccionar el tipo de compromiso de un catálogo predefinido, para estandarizar la gestión.      |
| **JD-04c** | Como **Jefe de División**, quiero establecer la prioridad del compromiso (Baja, Media, Alta, Urgente), para orientar al encargado. |
| **JD-04d** | Como **Jefe de División**, quiero reasignar un compromiso de un encargado a otro, para balancear cargas.                           |

### Verificación de Compromisos

| ID         | User Story                                                                                                                   |
| ---------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **JD-05a** | Como **Jefe de División**, quiero ver los compromisos completados por mi equipo pendientes de verificación, para revisarlos. |
| **JD-05b** | Como **Jefe de División**, quiero verificar el compromiso de un encargado y registrar mi aprobación, para cerrar el ciclo.   |
| **JD-05c** | Como **Jefe de División**, quiero agregar un comentario de retroalimentación al verificar, para comunicar observaciones.     |

### Registro de Problemas

| ID         | User Story                                                                                                                               |
| ---------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **JD-06a** | Como **Jefe de División**, quiero registrar un problema en una IPR de mi división, para documentar bloqueos detectados.                  |
| **JD-06b** | Como **Jefe de División**, quiero proponer una solución al registrar el problema, para orientar la resolución.                           |
| **JD-06c** | Como **Jefe de División**, quiero actualizar el estado de un problema a "En gestión" cuando se está trabajando, para reflejar el avance. |
| **JD-06d** | Como **Jefe de División**, quiero cerrar un problema registrando la solución aplicada, para mantener trazabilidad.                       |

### Coordinación Inter-Divisional

| ID         | User Story                                                                                                             |
| ---------- | ---------------------------------------------------------------------------------------------------------------------- |
| **JD-07a** | Como **Jefe de División**, quiero ver las IPR que comparto con otras divisiones, para coordinar acciones conjuntas.    |
| **JD-07b** | Como **Jefe de División**, quiero crear un compromiso asignado a otra división, para formalizar dependencias cruzadas. |
| **JD-07c** | Como **Jefe de División**, quiero ver los compromisos que otras divisiones tienen conmigo, para hacer seguimiento.     |

---

## 🟢 ROL: ENCARGADO OPERATIVO

### Mis Compromisos

| ID         | User Story                                                                                                                               |
| ---------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **EO-01a** | Como **Encargado Operativo**, quiero ver mi lista de compromisos ordenada por fecha límite, para priorizar mi trabajo diario.            |
| **EO-01b** | Como **Encargado Operativo**, quiero ver destacados mis compromisos vencidos al inicio de la lista, para abordarlos primero.             |
| **EO-01c** | Como **Encargado Operativo**, quiero filtrar mis compromisos por estado (Pendiente, En progreso, Completado), para organizar mi trabajo. |
| **EO-01d** | Como **Encargado Operativo**, quiero ver el tipo y descripción de cada compromiso, para entender qué debo hacer.                         |

### Mis IPR

| ID         | User Story                                                                                                              |
| ---------- | ----------------------------------------------------------------------------------------------------------------------- |
| **EO-02a** | Como **Encargado Operativo**, quiero ver la lista de IPR que tengo asignadas, para conocer mi cartera.                  |
| **EO-02b** | Como **Encargado Operativo**, quiero ver indicadores de alerta en mis IPR, para identificar las que requieren atención. |
| **EO-02c** | Como **Encargado Operativo**, quiero ver el último avance reportado de cada IPR, para saber si necesita actualización.  |

### Actualización de Compromisos

| ID         | User Story                                                                                                                         |
| ---------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **EO-03a** | Como **Encargado Operativo**, quiero cambiar el estado de mi compromiso a "En progreso", para reflejar que estoy trabajando en él. |
| **EO-03b** | Como **Encargado Operativo**, quiero agregar un comentario a mi compromiso, para documentar avances parciales.                     |
| **EO-03c** | Como **Encargado Operativo**, quiero adjuntar una referencia (ej: folio SGDOC) a mi compromiso, para respaldar mis acciones.       |

### Completar Compromisos

| ID         | User Story                                                                                                                                         |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **EO-04a** | Como **Encargado Operativo**, quiero marcar mi compromiso como "Completado", para indicar que terminé la tarea.                                    |
| **EO-04b** | Como **Encargado Operativo**, quiero agregar un comentario de cierre obligatorio, para explicar qué hice.                                          |
| **EO-04c** | Como **Encargado Operativo**, quiero recibir confirmación visual de que mi compromiso fue enviado a verificación, para tener certeza del registro. |

### Registrar Informe de Avance

| ID         | User Story                                                                                                                      |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **EO-05a** | Como **Encargado Operativo**, quiero registrar un nuevo informe de avance para una IPR, para actualizar el estado del proyecto. |
| **EO-05b** | Como **Encargado Operativo**, quiero ingresar el porcentaje de avance físico, para reflejar el progreso de la obra.             |
| **EO-05c** | Como **Encargado Operativo**, quiero ingresar el porcentaje de avance financiero, para reflejar la ejecución presupuestaria.    |
| **EO-05d** | Como **Encargado Operativo**, quiero agregar una descripción del avance, para contextualizar los números.                       |
| **EO-05e** | Como **Encargado Operativo**, quiero adjuntar un documento PDF del informe, para respaldar los datos.                           |
| **EO-05f** | Como **Encargado Operativo**, quiero adjuntar fotos de terreno, para evidenciar el avance físico.                               |

### Registrar Problemas

| ID         | User Story                                                                                                            |
| ---------- | --------------------------------------------------------------------------------------------------------------------- |
| **EO-06a** | Como **Encargado Operativo**, quiero registrar un problema detectado en una de mis IPR, para alertar sobre bloqueos.  |
| **EO-06b** | Como **Encargado Operativo**, quiero describir el problema en texto libre, para explicar la situación.                |
| **EO-06c** | Como **Encargado Operativo**, quiero seleccionar el tipo de impacto del problema, para que se priorice correctamente. |

### Ver Ficha IPR

| ID         | User Story                                                                                                            |
| ---------- | --------------------------------------------------------------------------------------------------------------------- |
| **EO-07a** | Como **Encargado Operativo**, quiero ver la ficha completa de una IPR, para consultar todos sus datos.                |
| **EO-07b** | Como **Encargado Operativo**, quiero ver los convenios asociados a la IPR, para entender la estructura financiera.    |
| **EO-07c** | Como **Encargado Operativo**, quiero ver las cuotas programadas y su estado de pago, para gestionar el flujo de caja. |
| **EO-07d** | Como **Encargado Operativo**, quiero ver los problemas abiertos de la IPR, para conocer los bloqueos actuales.        |

### Ver Historial de IPR

| ID         | User Story                                                                                                              |
| ---------- | ----------------------------------------------------------------------------------------------------------------------- |
| **EO-08a** | Como **Encargado Operativo**, quiero ver el historial de compromisos de una IPR, para entender las acciones pasadas.    |
| **EO-08b** | Como **Encargado Operativo**, quiero ver el historial de cambios de estado de cada compromiso, para auditar la gestión. |
| **EO-08c** | Como **Encargado Operativo**, quiero ver los informes de avance anteriores, para comparar progreso.                     |

---

## ⚙️ ROL: ADMINISTRADOR DEL SISTEMA

### Gestión de Divisiones

| ID         | User Story                                                                                                                       |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **AS-01a** | Como **Administrador del Sistema**, quiero crear una nueva división, para reflejar la estructura organizacional del GORE.        |
| **AS-01b** | Como **Administrador del Sistema**, quiero ingresar el nombre y descripción de la división, para identificarla correctamente.    |
| **AS-02a** | Como **Administrador del Sistema**, quiero editar el nombre de una división existente, para corregir errores o reflejar cambios. |
| **AS-02b** | Como **Administrador del Sistema**, quiero asignar un jefe a una división, para establecer la jerarquía.                         |
| **AS-02c** | Como **Administrador del Sistema**, quiero cambiar el jefe de una división, para reflejar rotaciones de personal.                |

### Gestión de Usuarios

| ID         | User Story                                                                                                                                             |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **AS-03a** | Como **Administrador del Sistema**, quiero crear un nuevo usuario con nombre, email y división, para darle acceso al sistema.                          |
| **AS-03b** | Como **Administrador del Sistema**, quiero asignar un rol al usuario (Admin Regional, Jefe División, Encargado), para definir sus permisos.            |
| **AS-03c** | Como **Administrador del Sistema**, quiero generar una contraseña temporal automática, para enviarla al nuevo usuario.                                 |
| **AS-04a** | Como **Administrador del Sistema**, quiero editar los datos de un usuario existente, para corregir información.                                        |
| **AS-04b** | Como **Administrador del Sistema**, quiero cambiar la división de un usuario, para reflejar traslados internos.                                        |
| **AS-04c** | Como **Administrador del Sistema**, quiero cambiar el rol de un usuario, para reflejar ascensos o cambios de función.                                  |
| **AS-05a** | Como **Administrador del Sistema**, quiero desactivar un usuario sin eliminarlo, para mantener el historial de auditoría.                              |
| **AS-05b** | Como **Administrador del Sistema**, quiero reactivar un usuario previamente desactivado, para restaurar su acceso.                                     |
| **AS-06a** | Como **Administrador del Sistema**, quiero restablecer la contraseña de un usuario, para resolver problemas de acceso.                                 |
| **AS-06b** | Como **Administrador del Sistema**, quiero que el sistema envíe un email con link de restablecimiento, para que el usuario defina su nueva contraseña. |

### Importación de Datos

| ID         | User Story                                                                                                                                          |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **AS-07a** | Como **Administrador del Sistema**, quiero importar IPR desde un archivo Excel, para cargar datos masivamente.                                      |
| **AS-07b** | Como **Administrador del Sistema**, quiero ver un preview de los datos antes de importar, para validar el contenido.                                |
| **AS-07c** | Como **Administrador del Sistema**, quiero mapear columnas del Excel a campos del sistema, para flexibilizar el formato de entrada.                 |
| **AS-07d** | Como **Administrador del Sistema**, quiero ver un reporte de errores de importación, para corregir registros fallidos.                              |
| **AS-08a** | Como **Administrador del Sistema**, quiero importar convenios desde un archivo Excel, para cargar datos financieros masivamente.                    |
| **AS-08b** | Como **Administrador del Sistema**, quiero que el sistema vincule automáticamente convenios a IPR existentes, para mantener integridad referencial. |

### Asignación Masiva

| ID         | User Story                                                                                                                                      |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **AS-09a** | Como **Administrador del Sistema**, quiero filtrar IPR por división para asignación masiva, para trabajar por segmentos.                        |
| **AS-09b** | Como **Administrador del Sistema**, quiero seleccionar múltiples IPR y asignarles un responsable común, para agilizar la configuración inicial. |
| **AS-09c** | Como **Administrador del Sistema**, quiero reasignar masivamente IPR de un usuario a otro, para gestionar salidas de personal.                  |

### Configuración de Alertas

| ID         | User Story                                                                                                                                |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **AS-10a** | Como **Administrador del Sistema**, quiero crear una regla de alerta con condiciones lógicas, para automatizar la detección de problemas. |
| **AS-10b** | Como **Administrador del Sistema**, quiero definir el nivel de la alerta (Info, Atención, Alto, Crítico), para priorizar su visibilidad.  |
| **AS-10c** | Como **Administrador del Sistema**, quiero especificar a quién notificar cuando se active la alerta, para asegurar la recepción.          |
| **AS-10d** | Como **Administrador del Sistema**, quiero editar reglas de alerta existentes, para ajustar umbrales según la experiencia operativa.      |
| **AS-10e** | Como **Administrador del Sistema**, quiero desactivar una regla de alerta sin eliminarla, para pausar notificaciones temporalmente.       |

### Logs y Monitoreo

| ID         | User Story                                                                                                       |
| ---------- | ---------------------------------------------------------------------------------------------------------------- |
| **AS-11a** | Como **Administrador del Sistema**, quiero ver los logs de actividad del sistema, para auditar operaciones.      |
| **AS-11b** | Como **Administrador del Sistema**, quiero filtrar logs por usuario, para investigar acciones específicas.       |
| **AS-11c** | Como **Administrador del Sistema**, quiero filtrar logs por fecha, para acotar investigaciones.                  |
| **AS-11d** | Como **Administrador del Sistema**, quiero ver errores del sistema destacados, para resolver problemas técnicos. |

### Gestión de Backups

| ID         | User Story                                                                                                                            |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **AS-12a** | Como **Administrador del Sistema**, quiero ver el estado de los backups automáticos, para verificar que están funcionando.            |
| **AS-12b** | Como **Administrador del Sistema**, quiero ver la fecha del último backup exitoso, para evaluar el riesgo de pérdida de datos.        |
| **AS-12c** | Como **Administrador del Sistema**, quiero iniciar un backup manual, para asegurar un punto de restauración antes de cambios mayores. |
| **AS-12d** | Como **Administrador del Sistema**, quiero restaurar el sistema desde un backup anterior, para recuperar datos en caso de desastre.   |

---

## 📊 Resumen Estadístico

| Rol                       | Total User Stories |
| ------------------------- | ------------------ |
| Administrador Regional    | **30**             |
| Jefe de División          | **22**             |
| Encargado Operativo       | **25**             |
| Administrador del Sistema | **31**             |
| **TOTAL**                 | **108**            |

---

> **Nota**: Estas user stories están diseñadas para ser atómicas y testables. Cada una representa una funcionalidad discreta que puede ser implementada y verificada independientemente.
