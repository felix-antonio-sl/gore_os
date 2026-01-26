# MODELO DE DATOS COMPLETO

  1. ENTIDADES FORMALES (ya existen en para_titi, se mantienen)

  -- Estas tablas YA EXISTEN, solo las referenciamos
  -- gore_inversion.iniciativa (IPR)
  -- gore_financiero.convenio
  -- gore_financiero.cuota

  -- NUEVA: Resolución (acto administrativo)
  CREATE TABLE gore_actos.resolucion (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      numero VARCHAR(20) NOT NULL,           -- RE-2026-0001
      tipo VARCHAR(30) NOT NULL,             -- EXENTA, AFECTA
      materia VARCHAR(100) NOT NULL,         -- Aprobación convenio, Modificación, etc.

      -- Vinculación                                                                                                    
      iniciativa_id UUID REFERENCES gore_inversion.iniciativa(id),                                                      
      convenio_id UUID REFERENCES gore_financiero.convenio(id),                                                         
                                                                                                                        
      -- Estado de tramitación                                                                                          
      estado VARCHAR(30) DEFAULT 'BORRADOR',  -- BORRADOR, EN_REVISION, FIRMADA, TRAMITADA, RECHAZADA                   
                                                                                                                        
      -- Fechas clave                                                                                                   
      fecha_elaboracion DATE,                                                                                           
      fecha_firma DATE,                                                                                                 
      fecha_total_tramitacion DATE,                                                                                     
                                                                                                                        
      -- Responsables                                                                                                   
      elaborado_por_id UUID REFERENCES gore_autenticacion.usuario(id),                                                  
      visado_por_id UUID REFERENCES gore_autenticacion.usuario(id),                                                     
      firmado_por VARCHAR(100),               -- Nombre del firmante (Gobernador, etc.)                                 
                                                                                                                        
      -- Contenido                                                                                                      
      considerandos TEXT,                                                                                               
      resuelvo TEXT,                                                                                                    
      documento_url VARCHAR(500),                                                                                       
                                                                                                                        
      -- Auditoría                                                                                                      
      created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                                                 
      updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP                                                                  
  );

  CREATE INDEX idx_resolucion_iniciativa ON gore_actos.resolucion(iniciativa_id);
  CREATE INDEX idx_resolucion_convenio ON gore_actos.resolucion(convenio_id);
  CREATE INDEX idx_resolucion_estado ON gore_actos.resolucion(estado);

  1. TRABAJO (unificado)

  -- Schema para trabajo unificado
  CREATE SCHEMA IF NOT EXISTS gore_trabajo;

  -- Tabla principal de trabajo
  CREATE TABLE gore_trabajo.item (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      codigo VARCHAR(20) NOT NULL UNIQUE,     -- IT-2026-00001

      -- Descripción                                                                                                    
      titulo VARCHAR(500) NOT NULL,                                                                                     
      descripcion TEXT,                                                                                                 
                                                                                                                        
      -- Jerarquía                                                                                                      
      padre_id UUID REFERENCES gore_trabajo.item(id),                                                                   
                                                                                                                        
      -- Responsabilidad                                                                                                
      responsable_id UUID NOT NULL REFERENCES gore_autenticacion.usuario(id),                                           
      division_id UUID REFERENCES gore_organizacion.division(id),                                                       
                                                                                                                        
      -- Estado (flujo único)                                                                                           
      estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',                                                                  
      -- PENDIENTE, EN_PROGRESO, BLOQUEADO, COMPLETADO, VERIFICADO, CANCELADO                                           
                                                                                                                        
      -- Verificación (para jefaturas)                                                                                  
      verificado_por_id UUID REFERENCES gore_autenticacion.usuario(id),                                                 
      verificado_en TIMESTAMPTZ,                                                                                        
                                                                                                                        
      -- Bloqueo                                                                                                        
      bloqueado_por TEXT,                                                                                               
      bloqueado_esperando_id UUID REFERENCES gore_trabajo.item(id),                                                     
                                                                                                                        
      -- Temporalidad                                                                                                   
      fecha_limite DATE,                                                                                                
      fecha_programada DATE,                                                                                            
                                                                                                                        
      -- Prioridad                                                                                                      
      prioridad VARCHAR(10) DEFAULT 'NORMAL',  -- URGENTE, NORMAL, BAJA                                                 
                                                                                                                        
      -- Vinculación a ENTIDADES FORMALES (el centro del modelo)                                                        
      iniciativa_id UUID REFERENCES gore_inversion.iniciativa(id),                                                      
      convenio_id UUID REFERENCES gore_financiero.convenio(id),                                                         
      resolucion_id UUID REFERENCES gore_actos.resolucion(id),                                                          
                                                                                                                        
      -- Vinculación a PROBLEMA (si este trabajo es para resolver un problema)                                          
      problema_id UUID,  -- FK se define después de crear tabla problema                                                
                                                                                                                        
      -- Contexto de proceso DIPIR                                                                                      
      proceso_ref VARCHAR(100),                                                                                         
      etapa_proceso VARCHAR(50),                                                                                        
                                                                                                                        
      -- Origen (de dónde vino este trabajo)                                                                            
      origen_tipo VARCHAR(30),                -- MANUAL, REUNION, PROBLEMA, ALERTA, SISTEMA                             
      origen_reunion_id UUID,                                                                                           
                                                                                                                        
      -- Metadatos                                                                                                      
      tags TEXT[],                                                                                                      
                                                                                                                        
      -- Auditoría                                                                                                      
      creado_por_id UUID NOT NULL REFERENCES gore_autenticacion.usuario(id),                                            
      created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                                                 
      updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                                                 
      completed_at TIMESTAMPTZ                                                                                          
  );

  -- Secuencia y trigger para código
  CREATE SEQUENCE gore_trabajo.item_seq;
  CREATE OR REPLACE FUNCTION gore_trabajo.gen_codigo()
  RETURNS TRIGGER AS $$
  BEGIN
      NEW.codigo := 'IT-' || TO_CHAR(CURRENT_DATE, 'YYYY') || '-' ||
                    LPAD(nextval('gore_trabajo.item_seq')::TEXT, 5, '0');
      RETURN NEW;
  END;
  $$ LANGUAGE plpgsql;

  CREATE TRIGGER trg_item_codigo
      BEFORE INSERT ON gore_trabajo.item
      FOR EACH ROW EXECUTE FUNCTION gore_trabajo.gen_codigo();

  -- Índices
  CREATE INDEX idx_item_responsable ON gore_trabajo.item(responsable_id, estado);
  CREATE INDEX idx_item_division ON gore_trabajo.item(division_id, estado);
  CREATE INDEX idx_item_padre ON gore_trabajo.item(padre_id);
  CREATE INDEX idx_item_iniciativa ON gore_trabajo.item(iniciativa_id) WHERE iniciativa_id IS NOT NULL;
  CREATE INDEX idx_item_convenio ON gore_trabajo.item(convenio_id) WHERE convenio_id IS NOT NULL;
  CREATE INDEX idx_item_problema ON gore_trabajo.item(problema_id) WHERE problema_id IS NOT NULL;
  CREATE INDEX idx_item_vencido ON gore_trabajo.item(fecha_limite)
      WHERE estado IN ('PENDIENTE', 'EN_PROGRESO') AND fecha_limite IS NOT NULL;

  -- Historial de trabajo
  CREATE TABLE gore_trabajo.item_historial (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      item_id UUID NOT NULL REFERENCES gore_trabajo.item(id),
      campo VARCHAR(50) NOT NULL,
      valor_anterior TEXT,
      valor_nuevo TEXT,
      usuario_id UUID NOT NULL REFERENCES gore_autenticacion.usuario(id),
      comentario TEXT,
      created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
  );

  CREATE INDEX idx_historial_item ON gore_trabajo.item_historial(item_id, created_at DESC);

  3. PROBLEMAS

  -- Problemas (situaciones que afectan el flujo)
  CREATE TABLE gore_trabajo.problema (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      codigo VARCHAR(20) NOT NULL UNIQUE,     -- PR-2026-00001

      -- Descripción
      descripcion TEXT NOT NULL,

      -- Clasificación
      tipo VARCHAR(30) NOT NULL,              -- TECNICO, FINANCIERO, ADMINISTRATIVO, LEGAL, COORDINACION, EXTERNO
      impacto VARCHAR(30) NOT NULL,           -- BLOQUEA_PAGO, RETRASA_OBRA, RETRASA_CONVENIO, RIESGO_RENDICION, OTRO
      impacto_descripcion TEXT,

      -- Vinculación a ENTIDADES FORMALES
      iniciativa_id UUID REFERENCES gore_inversion.iniciativa(id),
      convenio_id UUID REFERENCES gore_financiero.convenio(id),
      resolucion_id UUID REFERENCES gore_actos.resolucion(id),

      -- Estado
      estado VARCHAR(30) DEFAULT 'ABIERTO',   -- ABIERTO, EN_GESTION, RESUELTO, CERRADO_SIN_RESOLVER

      -- Detección
      detectado_por_id UUID NOT NULL REFERENCES gore_autenticacion.usuario(id),
      detectado_en TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

      -- Solución
      solucion_propuesta TEXT,
      solucion_aplicada TEXT,
      resuelto_por_id UUID REFERENCES gore_autenticacion.usuario(id),
      resuelto_en TIMESTAMPTZ,

      -- Auditoría
      created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
  );

  -- Secuencia y trigger
  CREATE SEQUENCE gore_trabajo.problema_seq;
  CREATE OR REPLACE FUNCTION gore_trabajo.gen_codigo_problema()
  RETURNS TRIGGER AS $$
  BEGIN
      NEW.codigo := 'PR-' || TO_CHAR(CURRENT_DATE, 'YYYY') || '-' ||
                    LPAD(nextval('gore_trabajo.problema_seq')::TEXT, 5, '0');
      RETURN NEW;
  END;
  $$ LANGUAGE plpgsql;

  CREATE TRIGGER trg_problema_codigo
      BEFORE INSERT ON gore_trabajo.problema
      FOR EACH ROW EXECUTE FUNCTION gore_trabajo.gen_codigo_problema();

  -- FK en item_trabajo para problema
  ALTER TABLE gore_trabajo.item
  ADD CONSTRAINT fk_item_problema
  FOREIGN KEY (problema_id) REFERENCES gore_trabajo.problema(id);

  -- Índices
  CREATE INDEX idx_problema_iniciativa ON gore_trabajo.problema(iniciativa_id);
  CREATE INDEX idx_problema_estado ON gore_trabajo.problema(estado) WHERE estado IN ('ABIERTO', 'EN_GESTION');

  -- Trigger: cuando se crea un problema, actualizar flag en iniciativa
  CREATE OR REPLACE FUNCTION gore_trabajo.sync_problema_iniciativa()
  RETURNS TRIGGER AS $$
  BEGIN
      IF NEW.iniciativa_id IS NOT NULL THEN
          UPDATE gore_inversion.iniciativa
          SET tiene_problemas_abiertos = EXISTS(
              SELECT 1 FROM gore_trabajo.problema
              WHERE iniciativa_id = NEW.iniciativa_id
              AND estado IN ('ABIERTO', 'EN_GESTION')
          )
          WHERE id = NEW.iniciativa_id;
      END IF;
      RETURN NEW;
  END;
  $$ LANGUAGE plpgsql;

  CREATE TRIGGER trg_problema_sync
      AFTER INSERT OR UPDATE ON gore_trabajo.problema
      FOR EACH ROW EXECUTE FUNCTION gore_trabajo.sync_problema_iniciativa();

  4. ALERTAS

  -- Alertas (notificaciones automáticas)
  CREATE TABLE gore_trabajo.alerta (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

      -- Target (qué entidad dispara la alerta)
      target_tipo VARCHAR(30) NOT NULL,       -- IPR, CONVENIO, RESOLUCION, ITEM, PROBLEMA
      target_id UUID NOT NULL,

      -- Para navegación rápida a IPR
      iniciativa_id UUID REFERENCES gore_inversion.iniciativa(id),

      -- Tipo y nivel
      tipo VARCHAR(50) NOT NULL,              -- CUOTA_VENCIDA, CONVENIO_POR_VENCER, TRABAJO_VENCIDO, etc.
      nivel VARCHAR(20) NOT NULL,             -- INFO, ATENCION, ALTO, CRITICO

      -- Mensaje
      mensaje TEXT NOT NULL,
      datos_contexto JSONB,

      -- Estado
      activa BOOLEAN DEFAULT TRUE,

      -- Atención
      atendida_por_id UUID REFERENCES gore_autenticacion.usuario(id),
      atendida_en TIMESTAMPTZ,
      accion_tomada TEXT,

      -- Auditoría
      generada_en TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
  );

  CREATE INDEX idx_alerta_activa ON gore_trabajo.alerta(activa, nivel) WHERE activa = TRUE;
  CREATE INDEX idx_alerta_iniciativa ON gore_trabajo.alerta(iniciativa_id) WHERE activa = TRUE;
  CREATE INDEX idx_alerta_target ON gore_trabajo.alerta(target_tipo, target_id);

  -- Tipos de alerta predefinidos
  COMMENT ON TABLE gore_trabajo.alerta IS '
  Tipos de alerta:
  - CUOTA_VENCIDA: Cuota de pago vencida
  - CUOTA_PROXIMA: Cuota próxima a vencer (7 días)
  - CONVENIO_POR_VENCER: Convenio próximo a vencer (30 días)
  - CONVENIO_VENCIDO: Convenio vencido
  - TRABAJO_VENCIDO: Item de trabajo vencido
  - TRABAJO_BLOQUEADO_LARGO: Item bloqueado por más de X días
  - PROBLEMA_SIN_GESTION: Problema abierto sin trabajo asignado
  - RENDICION_PENDIENTE: Rendición pendiente
  - OBRA_SIN_PAGO: Obra terminada sin pago completo
  ';

  5. USUARIOS CON ROLES

  -- Extensión de usuario para roles del sistema
  -- (asumiendo que gore_autenticacion.usuario ya existe)

  ALTER TABLE gore_autenticacion.usuario
  ADD COLUMN IF NOT EXISTS rol_sistema VARCHAR(30) DEFAULT 'ENCARGADO';
  -- ADMIN_SISTEMA, ADMIN_REGIONAL, JEFE_DIVISION, ENCARGADO

  COMMENT ON COLUMN gore_autenticacion.usuario.rol_sistema IS '
  Roles del sistema:
  - ADMIN_SISTEMA: Configura sistema, usuarios, importa datos
  - ADMIN_REGIONAL: Visión 360°, coordina divisiones, gestiona crisis
  - JEFE_DIVISION: Supervisa su división, verifica trabajo, asigna
  - ENCARGADO: Ejecuta trabajo, actualiza avances, reporta problemas
  ';

  -- Vista de permisos por rol
  CREATE VIEW gore_autenticacion.v_permisos_rol AS
  SELECT
      'ADMIN_SISTEMA' as rol,
      ARRAY['configurar_sistema', 'gestionar_usuarios', 'importar_datos', 'ver_logs', 'ver_todo', 'crear_trabajo',
  'asignar_trabajo'] as permisos
  UNION ALL
  SELECT
      'ADMIN_REGIONAL',
      ARRAY['ver_todo', 'crear_trabajo', 'asignar_trabajo', 'verificar_trabajo', 'gestionar_reuniones',
  'exportar_informes', 'escalar_problemas']
  UNION ALL
  SELECT
      'JEFE_DIVISION',
      ARRAY['ver_division', 'crear_trabajo', 'asignar_trabajo_division', 'verificar_trabajo_division',
  'registrar_problemas']
  UNION ALL
  SELECT
      'ENCARGADO',
      ARRAY['ver_mi_trabajo', 'actualizar_mi_trabajo', 'registrar_problemas', 'registrar_avances'];

  ---
  VISTAS ÚTILES

  -- Vista: Dashboard ejecutivo (para Admin Regional)
  CREATE VIEW gore_trabajo.v_dashboard_ejecutivo AS
  SELECT
      (SELECT COUNT(*) FROM gore_inversion.iniciativa) as total_ipr,
      (SELECT COUNT(*) FROM gore_inversion.iniciativa WHERE tiene_problemas_abiertos) as ipr_con_problemas,
      (SELECT COUNT(*) FROM gore_trabajo.problema WHERE estado IN ('ABIERTO', 'EN_GESTION')) as problemas_abiertos,
      (SELECT COUNT(*) FROM gore_trabajo.alerta WHERE activa AND nivel = 'CRITICO') as alertas_criticas,
      (SELECT COUNT(*) FROM gore_trabajo.item WHERE estado IN ('PENDIENTE', 'EN_PROGRESO') AND fecha_limite <
  CURRENT_DATE) as trabajo_vencido,
      (SELECT COUNT(*) FROM gore_trabajo.item WHERE estado = 'BLOQUEADO') as trabajo_bloqueado;

  -- Vista: Trabajo por usuario con contexto
  CREATE VIEW gore_trabajo.v_mi_trabajo AS
  SELECT
      i.*,
      u.nombre_completo as responsable_nombre,
      d.nombre as division_nombre,
      -- Contexto de entidades
      ini.codigo_interno as ipr_codigo,
      ini.nombre as ipr_nombre,
      ini.nivel_alerta as ipr_nivel_alerta,
      conv.numero as convenio_numero,
      res.numero as resolucion_numero,
      -- Contexto de problema
      p.codigo as problema_codigo,
      p.descripcion as problema_desc,
      -- Jerarquía
      padre.codigo as padre_codigo,
      padre.titulo as padre_titulo,
      -- Métricas
      (SELECT COUNT(*) FROM gore_trabajo.item h WHERE h.padre_id = i.id) as total_hijos,
      (SELECT COUNT(*) FROM gore_trabajo.item h WHERE h.padre_id = i.id AND h.estado = 'COMPLETADO') as
  hijos_completados,
      -- Tiempo
      CASE
          WHEN i.estado IN ('PENDIENTE', 'EN_PROGRESO') AND i.fecha_limite < CURRENT_DATE
          THEN CURRENT_DATE - i.fecha_limite
          ELSE 0
      END as dias_vencido
  FROM gore_trabajo.item i
  LEFT JOIN gore_autenticacion.usuario u ON i.responsable_id = u.id
  LEFT JOIN gore_organizacion.division d ON i.division_id = d.id
  LEFT JOIN gore_inversion.iniciativa ini ON i.iniciativa_id = ini.id
  LEFT JOIN gore_financiero.convenio conv ON i.convenio_id = conv.id
  LEFT JOIN gore_actos.resolucion res ON i.resolucion_id = res.id
  LEFT JOIN gore_trabajo.problema p ON i.problema_id = p.id
  LEFT JOIN gore_trabajo.item padre ON i.padre_id = padre.id;

  -- Vista: Estado de IPR con trabajo y problemas
  CREATE VIEW gore_trabajo.v_ipr_completa AS
  SELECT
      i.*,
      -- Trabajo asociado
      (SELECT COUNT(*) FROM gore_trabajo.item t WHERE t.iniciativa_id = i.id) as total_trabajo,
      (SELECT COUNT(*) FROM gore_trabajo.item t WHERE t.iniciativa_id = i.id AND t.estado = 'COMPLETADO') as
  trabajo_completado,
      (SELECT COUNT(*) FROM gore_trabajo.item t WHERE t.iniciativa_id = i.id AND t.estado = 'BLOQUEADO') as
  trabajo_bloqueado,
      (SELECT COUNT(*) FROM gore_trabajo.item t WHERE t.iniciativa_id = i.id AND t.estado IN ('PENDIENTE',
  'EN_PROGRESO') AND t.fecha_limite < CURRENT_DATE) as trabajo_vencido,
      -- Problemas
      (SELECT COUNT(*) FROM gore_trabajo.problema p WHERE p.iniciativa_id = i.id AND p.estado IN ('ABIERTO',
  'EN_GESTION')) as problemas_abiertos,
      -- Alertas
      (SELECT COUNT(*) FROM gore_trabajo.alerta a WHERE a.iniciativa_id = i.id AND a.activa AND a.nivel = 'CRITICO') as
  alertas_criticas,
      -- Convenios
      (SELECT COUNT(*) FROM gore_financiero.convenio c WHERE c.iniciativa_id = i.id) as total_convenios
  FROM gore_inversion.iniciativa i;

  ---
  SERVICIO INTEGRADO

  # app/services/trabajo_service.py

  from datetime import date, datetime, timedelta
  from sqlalchemy import func, case, and_, or_
  from app.extensions import db
  from app.models import ItemTrabajo, Problema, Alerta, Iniciativa, Convenio, Resolucion, Usuario

  class TrabajoService:
      """
      Servicio unificado de trabajo.
      Integra: Entidades formales + Trabajo + Problemas + Alertas
      """

      # =========================================================================
      # TRABAJO
      # =========================================================================

      @staticmethod
      def crear(titulo: str, responsable_id: str, creado_por_id: str,
                descripcion: str = None, padre_id: str = None,
                fecha_limite: date = None, prioridad: str = 'NORMAL',
                iniciativa_id: str = None, convenio_id: str = None,
                resolucion_id: str = None, problema_id: str = None,
                proceso_ref: str = None, origen_tipo: str = 'MANUAL',
                tags: list = None) -> ItemTrabajo:
          """Crea un ítem de trabajo vinculado a entidades formales."""

          item = ItemTrabajo(
              titulo=titulo,
              descripcion=descripcion,
              responsable_id=responsable_id,
              padre_id=padre_id,
              fecha_limite=fecha_limite,
              prioridad=prioridad,
              iniciativa_id=iniciativa_id,
              convenio_id=convenio_id,
              resolucion_id=resolucion_id,
              problema_id=problema_id,
              proceso_ref=proceso_ref,
              origen_tipo=origen_tipo,
              tags=tags or [],
              creado_por_id=creado_por_id
          )

          # Derivar división del responsable
          responsable = Usuario.query.get(responsable_id)
          if responsable:
              item.division_id = responsable.division_id

          # Heredar vinculación del padre si no se especificó
          if padre_id and not iniciativa_id:
              padre = ItemTrabajo.query.get(padre_id)
              if padre:
                  item.iniciativa_id = item.iniciativa_id or padre.iniciativa_id
                  item.convenio_id = item.convenio_id or padre.convenio_id
                  item.proceso_ref = item.proceso_ref or padre.proceso_ref

          db.session.add(item)
          db.session.commit()

          return item

      @staticmethod
      def captura_rapida(titulo: str, usuario_id: str,
                         iniciativa_id: str = None) -> ItemTrabajo:
          """Captura rápida de trabajo."""
          return TrabajoService.crear(
              titulo=titulo,
              responsable_id=usuario_id,
              creado_por_id=usuario_id,
              iniciativa_id=iniciativa_id,
              origen_tipo='MANUAL'
          )

      @staticmethod
      def completar(item_id: str, usuario_id: str, comentario: str = None):
          """Marca trabajo como completado."""
          item = ItemTrabajo.query.get_or_404(item_id)
          item.estado = 'COMPLETADO'
          item.completed_at = datetime.utcnow()
          item.updated_at = datetime.utcnow()

          # Registrar en historial
          TrabajoService._registrar_historial(
              item_id, 'estado', item.estado, 'COMPLETADO', usuario_id, comentario
          )

          db.session.commit()
          return item

      @staticmethod
      def verificar(item_id: str, usuario_id: str, comentario: str = None):
          """Jefatura verifica trabajo completado."""
          item = ItemTrabajo.query.get_or_404(item_id)

          if item.estado != 'COMPLETADO':
              raise ValueError("Solo se puede verificar trabajo completado")

          item.estado = 'VERIFICADO'
          item.verificado_por_id = usuario_id
          item.verificado_en = datetime.utcnow()

          TrabajoService._registrar_historial(
              item_id, 'estado', 'COMPLETADO', 'VERIFICADO', usuario_id, comentario
          )

          db.session.commit()
          return item

      @staticmethod
      def bloquear(item_id: str, usuario_id: str, motivo: str,
                   esperando_id: str = None):
          """Marca trabajo como bloqueado."""
          item = ItemTrabajo.query.get_or_404(item_id)
          item.estado = 'BLOQUEADO'
          item.bloqueado_por = motivo
          item.bloqueado_esperando_id = esperando_id
          item.updated_at = datetime.utcnow()

          TrabajoService._registrar_historial(
              item_id, 'estado', item.estado, 'BLOQUEADO', usuario_id, motivo
          )

          db.session.commit()
          return item

      @staticmethod
      def reasignar(item_id: str, nuevo_responsable_id: str,
                    usuario_id: str, comentario: str = None):
          """Reasigna trabajo a otro responsable."""
          item = ItemTrabajo.query.get_or_404(item_id)
          anterior = item.responsable_id

          item.responsable_id = nuevo_responsable_id
          # Actualizar división
          responsable = Usuario.query.get(nuevo_responsable_id)
          if responsable:
              item.division_id = responsable.division_id

          item.updated_at = datetime.utcnow()

          TrabajoService._registrar_historial(
              item_id, 'responsable_id', str(anterior),
              str(nuevo_responsable_id), usuario_id, comentario
          )

          db.session.commit()
          return item

      # =========================================================================
      # CONSULTAS DE TRABAJO
      # =========================================================================

      @staticmethod
      def mi_trabajo(usuario_id: str, solo_activos: bool = True):
          """Trabajo asignado a un usuario."""
          query = ItemTrabajo.query.filter_by(responsable_id=usuario_id)

          if solo_activos:
              query = query.filter(
                  ItemTrabajo.estado.in_(['PENDIENTE', 'EN_PROGRESO', 'BLOQUEADO'])
              )

          return query.order_by(
              case(
                  (ItemTrabajo.prioridad == 'URGENTE', 1),
                  (ItemTrabajo.estado == 'BLOQUEADO', 2),
                  (ItemTrabajo.prioridad == 'NORMAL', 3),
                  else_=4
              ),
              ItemTrabajo.fecha_limite.asc().nullslast()
          ).all()

      @staticmethod
      def trabajo_division(division_id: str, solo_activos: bool = True):
          """Trabajo de una división completa."""
          query = ItemTrabajo.query.filter_by(division_id=division_id)

          if solo_activos:
              query = query.filter(
                  ItemTrabajo.estado.in_(['PENDIENTE', 'EN_PROGRESO', 'BLOQUEADO'])
              )

          return query.order_by(
              ItemTrabajo.responsable_id,
              ItemTrabajo.prioridad,
              ItemTrabajo.fecha_limite.asc().nullslast()
          ).all()

      @staticmethod
      def trabajo_ipr(iniciativa_id: str) -> dict:
          """Trabajo asociado a una IPR (árbol completo)."""
          items = ItemTrabajo.query.filter_by(
              iniciativa_id=iniciativa_id
          ).order_by(ItemTrabajo.created_at).all()

          # Construir árbol
          raices = [i for i in items if i.padre_id is None]

          def construir_hijos(padre_id):
              hijos = [i for i in items if i.padre_id == padre_id]
              for hijo in hijos:
                  hijo.hijos = construir_hijos(hijo.id)
              return hijos

          for raiz in raices:
              raiz.hijos = construir_hijos(raiz.id)

          return {
              'items': raices,
              'total': len(items),
              'completados': len([i for i in items if i.estado in ('COMPLETADO', 'VERIFICADO')]),
              'bloqueados': len([i for i in items if i.estado == 'BLOQUEADO']),
              'vencidos': len([i for i in items if i.estado in ('PENDIENTE', 'EN_PROGRESO')
                             and i.fecha_limite and i.fecha_limite < date.today()])
          }

      @staticmethod
      def trabajo_vencido(division_id: str = None, usuario_id: str = None):
          """Trabajo vencido."""
          query = ItemTrabajo.query.filter(
              ItemTrabajo.estado.in_(['PENDIENTE', 'EN_PROGRESO']),
              ItemTrabajo.fecha_limite < date.today()
          )

          if division_id:
              query = query.filter_by(division_id=division_id)
          if usuario_id:
              query = query.filter_by(responsable_id=usuario_id)

          return query.order_by(ItemTrabajo.fecha_limite).all()

      @staticmethod
      def trabajo_por_verificar(division_id: str):
          """Trabajo completado pendiente de verificación."""
          return ItemTrabajo.query.filter_by(
              division_id=division_id,
              estado='COMPLETADO'
          ).order_by(ItemTrabajo.completed_at).all()

      # =========================================================================
      # PROBLEMAS
      # =========================================================================

      @staticmethod
      def registrar_problema(descripcion: str, tipo: str, impacto: str,
                             detectado_por_id: str, iniciativa_id: str = None,
                             convenio_id: str = None,
                             impacto_descripcion: str = None) -> Problema:
          """Registra un problema/nudo."""
          problema = Problema(
              descripcion=descripcion,
              tipo=tipo,
              impacto=impacto,
              impacto_descripcion=impacto_descripcion,
              iniciativa_id=iniciativa_id,
              convenio_id=convenio_id,
              detectado_por_id=detectado_por_id
          )

          db.session.add(problema)
          db.session.commit()

          # Actualizar nivel de alerta de la IPR si aplica
          if iniciativa_id:
              TrabajoService._actualizar_nivel_alerta_ipr(iniciativa_id)

          return problema

      @staticmethod
      def resolver_problema(problema_id: str, usuario_id: str,
                            solucion_aplicada: str) -> Problema:
          """Marca problema como resuelto."""
          problema = Problema.query.get_or_404(problema_id)
          problema.estado = 'RESUELTO'
          problema.solucion_aplicada = solucion_aplicada
          problema.resuelto_por_id = usuario_id
          problema.resuelto_en = datetime.utcnow()

          db.session.commit()

          # Actualizar nivel de alerta de la IPR
          if problema.iniciativa_id:
              TrabajoService._actualizar_nivel_alerta_ipr(problema.iniciativa_id)

          return problema

      @staticmethod
      def problemas_abiertos(division_id: str = None, iniciativa_id: str = None):
          """Problemas abiertos o en gestión."""
          query = Problema.query.filter(
              Problema.estado.in_(['ABIERTO', 'EN_GESTION'])
          )

          if iniciativa_id:
              query = query.filter_by(iniciativa_id=iniciativa_id)

          # Si es por división, filtrar por IPR de la división
          if division_id:
              query = query.join(
                  Iniciativa, Problema.iniciativa_id == Iniciativa.id
              ).filter(Iniciativa.division_responsable_id == division_id)

          return query.order_by(
              case(
                  (Problema.impacto == 'BLOQUEA_PAGO', 1),
                  (Problema.impacto == 'RETRASA_OBRA', 2),
                  else_=3
              ),
              Problema.detectado_en.asc()
          ).all()

      @staticmethod
      def crear_trabajo_desde_problema(problema_id: str, titulo: str,
                                        responsable_id: str, creado_por_id: str,
                                        fecha_limite: date = None) -> ItemTrabajo:
          """Crea trabajo para resolver un problema."""
          problema = Problema.query.get_or_404(problema_id)

          # Cambiar estado del problema a EN_GESTION
          if problema.estado == 'ABIERTO':
              problema.estado = 'EN_GESTION'

          item = TrabajoService.crear(
              titulo=titulo,
              responsable_id=responsable_id,
              creado_por_id=creado_por_id,
              fecha_limite=fecha_limite,
              problema_id=problema_id,
              iniciativa_id=problema.iniciativa_id,
              convenio_id=problema.convenio_id,
              origen_tipo='PROBLEMA'
          )

          db.session.commit()
          return item

      # =========================================================================
      # ALERTAS
      # =========================================================================

      @staticmethod
      def alertas_activas(division_id: str = None, nivel_minimo: str = None,
                          limite: int = 20):
          """Alertas activas."""
          query = Alerta.query.filter_by(activa=True)

          if nivel_minimo:
              niveles = {'INFO': 1, 'ATENCION': 2, 'ALTO': 3, 'CRITICO': 4}
              query = query.filter(
                  case(
                      (Alerta.nivel == 'CRITICO', 4),
                      (Alerta.nivel == 'ALTO', 3),
                      (Alerta.nivel == 'ATENCION', 2),
                      else_=1
                  ) >= niveles.get(nivel_minimo, 1)
              )

          if division_id:
              # Filtrar por IPR de la división
              query = query.join(
                  Iniciativa, Alerta.iniciativa_id == Iniciativa.id
              ).filter(Iniciativa.division_responsable_id == division_id)

          return query.order_by(
              case(
                  (Alerta.nivel == 'CRITICO', 1),
                  (Alerta.nivel == 'ALTO', 2),
                  (Alerta.nivel == 'ATENCION', 3),
                  else_=4
              ),
              Alerta.generada_en.desc()
          ).limit(limite).all()

      @staticmethod
      def atender_alerta(alerta_id: str, usuario_id: str,
                         accion_tomada: str) -> Alerta:
          """Marca alerta como atendida."""
          alerta = Alerta.query.get_or_404(alerta_id)
          alerta.activa = False
          alerta.atendida_por_id = usuario_id
          alerta.atendida_en = datetime.utcnow()
          alerta.accion_tomada = accion_tomada

          db.session.commit()
          return alerta

      # =========================================================================
      # DASHBOARDS
      # =========================================================================

      @staticmethod
      def dashboard_ejecutivo():
          """Dashboard para Administrador Regional."""
          hoy = date.today()
          hace_7_dias = hoy - timedelta(days=7)

          return {
              # IPR
              'total_ipr': Iniciativa.query.count(),
              'ipr_con_problemas': Iniciativa.query.filter_by(
                  tiene_problemas_abiertos=True
              ).count(),

              # Problemas
              'problemas_abiertos': Problema.query.filter(
                  Problema.estado.in_(['ABIERTO', 'EN_GESTION'])
              ).count(),
              'problemas_criticos': Problema.query.filter(
                  Problema.estado.in_(['ABIERTO', 'EN_GESTION']),
                  Problema.impacto.in_(['BLOQUEA_PAGO', 'RETRASA_OBRA'])
              ).count(),

              # Trabajo
              'trabajo_vencido': ItemTrabajo.query.filter(
                  ItemTrabajo.estado.in_(['PENDIENTE', 'EN_PROGRESO']),
                  ItemTrabajo.fecha_limite < hoy
              ).count(),
              'trabajo_bloqueado': ItemTrabajo.query.filter_by(
                  estado='BLOQUEADO'
              ).count(),
              'trabajo_por_verificar': ItemTrabajo.query.filter_by(
                  estado='COMPLETADO'
              ).count(),

              # Alertas
              'alertas_criticas': Alerta.query.filter(
                  Alerta.activa == True,
                  Alerta.nivel == 'CRITICO'
              ).count(),

              # Tendencias (última semana)
              'problemas_nuevos_semana': Problema.query.filter(
                  Problema.detectado_en >= hace_7_dias
              ).count(),
              'problemas_resueltos_semana': Problema.query.filter(
                  Problema.resuelto_en >= hace_7_dias
              ).count(),
              'trabajo_completado_semana': ItemTrabajo.query.filter(
                  ItemTrabajo.completed_at >= hace_7_dias
              ).count()
          }

      @staticmethod
      def dashboard_division(division_id: str):
          """Dashboard para Jefe de División."""
          hoy = date.today()

          # Trabajo por estado
          trabajo = db.session.query(
              ItemTrabajo.estado,
              func.count(ItemTrabajo.id)
          ).filter_by(division_id=division_id).group_by(
              ItemTrabajo.estado
          ).all()

          # Trabajo por responsable
          por_responsable = db.session.query(
              Usuario.nombre_completo,
              func.count(ItemTrabajo.id).label('total'),
              func.sum(case((ItemTrabajo.fecha_limite < hoy, 1), else_=0)).label('vencidos')
          ).join(
              ItemTrabajo, ItemTrabajo.responsable_id == Usuario.id
          ).filter(
              ItemTrabajo.division_id == division_id,
              ItemTrabajo.estado.in_(['PENDIENTE', 'EN_PROGRESO', 'BLOQUEADO'])
          ).group_by(Usuario.id, Usuario.nombre_completo).all()

          return {
              'trabajo_por_estado': {estado: count for estado, count in trabajo},
              'por_responsable': [
                  {'nombre': r[0], 'total': r[1], 'vencidos': r[2]}
                  for r in por_responsable
              ],
              'trabajo_vencido': ItemTrabajo.query.filter(
                  ItemTrabajo.division_id == division_id,
                  ItemTrabajo.estado.in_(['PENDIENTE', 'EN_PROGRESO']),
                  ItemTrabajo.fecha_limite < hoy
              ).count(),
              'por_verificar': ItemTrabajo.query.filter_by(
                  division_id=division_id,
                  estado='COMPLETADO'
              ).count()
          }

      @staticmethod
      def dashboard_personal(usuario_id: str):
          """Dashboard personal para Encargado."""
          hoy = date.today()

          return {
              'pendientes': ItemTrabajo.query.filter_by(
                  responsable_id=usuario_id, estado='PENDIENTE'
              ).count(),
              'en_progreso': ItemTrabajo.query.filter_by(
                  responsable_id=usuario_id, estado='EN_PROGRESO'
              ).count(),
              'bloqueados': ItemTrabajo.query.filter_by(
                  responsable_id=usuario_id, estado='BLOQUEADO'
              ).count(),
              'vencidos': ItemTrabajo.query.filter(
                  ItemTrabajo.responsable_id == usuario_id,
                  ItemTrabajo.estado.in_(['PENDIENTE', 'EN_PROGRESO']),
                  ItemTrabajo.fecha_limite < hoy
              ).count(),
              'completados_semana': ItemTrabajo.query.filter(
                  ItemTrabajo.responsable_id == usuario_id,
                  ItemTrabajo.completed_at >= hoy - timedelta(days=7)
              ).count(),
              'mis_ipr': Iniciativa.query.filter_by(
                  responsable_id=usuario_id
              ).count()
          }

      # =========================================================================
      # UTILIDADES
      # =========================================================================

      @staticmethod
      def _registrar_historial(item_id, campo, anterior, nuevo, usuario_id, comentario):
          from app.models import ItemHistorial
          historial = ItemHistorial(
              item_id=item_id,
              campo=campo,
              valor_anterior=str(anterior) if anterior else None,
              valor_nuevo=str(nuevo),
              usuario_id=usuario_id,
              comentario=comentario
          )
          db.session.add(historial)

      @staticmethod
      def _actualizar_nivel_alerta_ipr(iniciativa_id):
          """Actualiza nivel de alerta de una IPR según sus problemas."""
          problemas = Problema.query.filter(
              Problema.iniciativa_id == iniciativa_id,
              Problema.estado.in_(['ABIERTO', 'EN_GESTION'])
          ).all()

          iniciativa = Iniciativa.query.get(iniciativa_id)

          if any(p.impacto in ('BLOQUEA_PAGO', 'RETRASA_OBRA') for p in problemas):
              iniciativa.nivel_alerta = 'CRITICO'
          elif any(p.impacto in ('RETRASA_CONVENIO', 'RIESGO_RENDICION') for p in problemas):
              iniciativa.nivel_alerta = 'ATENCION'
          elif problemas:
              iniciativa.nivel_alerta = 'ATENCION'
          else:
              iniciativa.nivel_alerta = 'NORMAL'

  ---
  MAPEO A CASOS DE USO
  ┌───────┬───────────────────────────┬─────────────────────────────────────────┬────────────────┐
  │  ID   │        Caso de Uso        │              Método/Vista               │      Rol       │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ AR-01 │ Ver dashboard ejecutivo   │ dashboard_ejecutivo()                   │ ADMIN_REGIONAL │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ AR-02 │ Revisar nudos críticos    │ problemas_abiertos() + filtro crítico   │ ADMIN_REGIONAL │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ AR-03 │ Preparar reunión semanal  │ Dashboard + alertas + trabajo vencido   │ ADMIN_REGIONAL │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ AR-04 │ Conducir reunión          │ crear() con origen_tipo='REUNION'       │ ADMIN_REGIONAL │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ AR-05 │ Verificar trabajo         │ verificar()                             │ ADMIN_REGIONAL │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ AR-06 │ Entrevistar responsable   │ trabajo_ipr() + mi_trabajo()            │ ADMIN_REGIONAL │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ AR-07 │ Generar informe           │ InformeService (gap cerrado antes)      │ ADMIN_REGIONAL │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ AR-08 │ Ver cumplimiento división │ dashboard_division() por cada una       │ ADMIN_REGIONAL │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ JD-01 │ Ver resumen división      │ dashboard_division()                    │ JEFE_DIVISION  │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ JD-02 │ Ver estado equipo         │ trabajo_division() agrupado             │ JEFE_DIVISION  │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ JD-03 │ Ver trabajo vencido       │ trabajo_vencido(division_id)            │ JEFE_DIVISION  │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ JD-04 │ Asignar trabajo           │ crear() + reasignar()                   │ JEFE_DIVISION  │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ JD-05 │ Verificar trabajo         │ verificar()                             │ JEFE_DIVISION  │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ JD-06 │ Registrar problema        │ registrar_problema()                    │ JEFE_DIVISION  │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ JD-07 │ Coordinar división        │ Trabajo con division_id diferente       │ JEFE_DIVISION  │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ EO-01 │ Ver mi trabajo            │ mi_trabajo()                            │ ENCARGADO      │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ EO-02 │ Ver mis IPR               │ Iniciativa filtrado por responsable     │ ENCARGADO      │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ EO-03 │ Actualizar trabajo        │ Cambiar estado, comentar                │ ENCARGADO      │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ EO-04 │ Completar trabajo         │ completar()                             │ ENCARGADO      │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ EO-05 │ Registrar avance          │ InformeAvance existente + crear trabajo │ ENCARGADO      │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ EO-06 │ Registrar problema        │ registrar_problema()                    │ ENCARGADO      │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ EO-07 │ Ver ficha IPR             │ trabajo_ipr() + datos IPR               │ ENCARGADO      │
  ├───────┼───────────────────────────┼─────────────────────────────────────────┼────────────────┤
  │ EO-08 │ Ver historial             │ ItemHistorial query                     │ ENCARGADO      │
  └───────┴───────────────────────────┴─────────────────────────────────────────┴────────────────┘
  ---
  RESUMEN FINAL

  ┌─────────────────────────────────────────────────────────────────────────────┐
  │                    MODELO INTEGRADO GOREOS - FINAL                          │
  ├─────────────────────────────────────────────────────────────────────────────┤
  │                                                                             │
  │  ENTIDADES FORMALES (el centro):                                            │
  │  ┌─────────┐     ┌─────────┐     ┌─────────────┐                           │
  │  │   IPR   │────▶│CONVENIO │────▶│ RESOLUCIÓN  │                           │
  │  └─────────┘     └─────────┘     └─────────────┘                           │
  │       │               │                │                                    │
  │       └───────────────┴────────────────┴───────────┐                       │
  │                                                     │                       │
  │  TRABAJO (unificado, cualquier escala):            │                       │
  │  ┌─────────────────────────────────────────────────┴───────────────────┐   │
  │  │  ITEM DE TRABAJO                                                     │   │
  │  │  • Vinculado a: IPR, Convenio, Resolución, Problema                 │   │
  │  │  • Jerarquía natural                                                 │   │
  │  │  • Un solo flujo: PENDIENTE→EN_PROGRESO→COMPLETADO→VERIFICADO       │   │
  │  └─────────────────────────────────────────────────────────────────────┘   │
  │                                                                             │
  │  PROBLEMAS (nudos que afectan el flujo):                                   │
  │  ┌─────────────────────────────────────────────────────────────────────┐   │
  │  │  • Tipo: TECNICO, FINANCIERO, ADMINISTRATIVO, LEGAL, etc.           │   │
  │  │  • Impacto: BLOQUEA_PAGO, RETRASA_OBRA, etc.                        │   │
  │  │  • Genera trabajo para resolverse                                    │   │
  │  └─────────────────────────────────────────────────────────────────────┘   │
  │                                                                             │
  │  ALERTAS (notificaciones automáticas):                                     │
  │  ┌─────────────────────────────────────────────────────────────────────┐   │
  │  │  • Nivel: INFO, ATENCION, ALTO, CRITICO                             │   │
  │  │  • Apuntan a: IPR, Convenio, ItemTrabajo, Problema                  │   │
  │  └─────────────────────────────────────────────────────────────────────┘   │
  │                                                                             │
  │  USUARIOS (roles diferenciados):                                           │
  │  ┌─────────────────────────────────────────────────────────────────────┐   │
  │  │  ADMIN_SISTEMA → ADMIN_REGIONAL → JEFE_DIVISION → ENCARGADO         │   │
  │  │  (configura)     (visión 360°)    (supervisa)      (ejecuta)        │   │
  │  └─────────────────────────────────────────────────────────────────────┘   │
  │                                                                             │
  │  COBERTURA:                                                                 │
  │  ✅ 35 casos de uso originales                                             │
  │  ✅ Entidades formales: IPR, Convenio, Resolución                          │
  │  ✅ Problemas y Alertas                                                     │
  │  ✅ Roles diferenciados                                                     │
  │  ✅ Modelo unificado de trabajo                                             │
  │  ✅ Simplicidad mantenida                                                   │
  │                                                                             │
  └─────────────────────────────────────────────────────────────────────────────┘

  ¿Este modelo integrado captura correctamente lo que necesitas?

✻ Churned for 3m 5s

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
❯
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ? for shortcuts                                                                                      ⧉ In gestion.md  
                                                                                   Context left until auto-compact: 8%  
