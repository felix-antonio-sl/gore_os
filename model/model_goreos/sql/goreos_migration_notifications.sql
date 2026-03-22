-- Migration: Create core.notification table for in-app notifications
-- Increment 1: plumbing only (table + index). Integration with event sources in increment 2.

BEGIN;

CREATE TABLE IF NOT EXISTS core.notification (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES core."user"(id),
    title           VARCHAR(200) NOT NULL,
    body            TEXT,
    category        VARCHAR(50) NOT NULL,   -- 'alerta', 'sla', 'escalamiento', 'compromiso', 'rendicion', 'firma', 'sistema'
    entity_type     VARCHAR(50),            -- 'core.ipr', 'core.agreement', etc.
    entity_id       UUID,
    link            VARCHAR(500),           -- frontend deep link e.g. '/ipr/{id}?tab=alertas'
    read_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_notification_user
    ON core.notification(user_id, read_at, created_at DESC)
    WHERE deleted_at IS NULL;

-- Seed sample notifications for admin user
INSERT INTO core.notification (user_id, title, body, category, entity_type, link)
SELECT u.id,
       'SLA vencido: rendicion DEMO-R-RND-001',
       'La rendicion ha superado el plazo de 7 dias en fase EN_REVISION_RTF.',
       'sla',
       'core.rendition',
       '/datos?dominio=rendiciones'
FROM core."user" u WHERE u.email = 'admin@goreos.cl';

INSERT INTO core.notification (user_id, title, body, category, entity_type, link)
SELECT u.id,
       'Alerta critica: IPR DEMO-R-INF-001',
       'El proyecto de infraestructura presenta retraso superior a 90 dias.',
       'alerta',
       'core.ipr',
       '/ipr'
FROM core."user" u WHERE u.email = 'admin@goreos.cl';

INSERT INTO core.notification (user_id, title, body, category, entity_type, link)
SELECT u.id,
       'Escalamiento nivel 2: ESC-2026-0012',
       'Se ha escalado a nivel JEFE_DIVISION por incumplimiento de plazo.',
       'escalamiento',
       'core.dgi_escalation',
       '/escalamiento'
FROM core."user" u WHERE u.email = 'admin@goreos.cl';

INSERT INTO core.notification (user_id, title, body, category, entity_type, link)
SELECT u.id,
       'Compromiso vencido: COMP-2026-0045',
       'El compromiso lleva 5 dias de retraso sin actualizacion.',
       'compromiso',
       'core.operational_commitment',
       '/compromisos'
FROM core."user" u WHERE u.email = 'admin@goreos.cl';

INSERT INTO core.notification (user_id, title, body, category, entity_type, link)
SELECT u.id,
       'Rendicion pendiente: convenio CNV-2026-018',
       'La cuota 3 del convenio requiere rendicion dentro de los proximos 7 dias.',
       'rendicion',
       'core.agreement',
       '/convenios'
FROM core."user" u WHERE u.email = 'admin@goreos.cl';

INSERT INTO core.notification (user_id, title, body, category, entity_type, link)
SELECT u.id,
       'Firma pendiente: Decreto DEMO-R-DEC-003',
       'El acto administrativo esta en estado VISADO esperando firma del Gobernador.',
       'firma',
       'core.administrative_act',
       '/actos'
FROM core."user" u WHERE u.email = 'admin@goreos.cl';

INSERT INTO core.notification (user_id, title, body, category, entity_type, link)
SELECT u.id,
       'Mantencion programada del sistema',
       'GORE_OS estara en mantencion el sabado 29 de marzo entre 22:00 y 02:00.',
       'sistema',
       NULL,
       NULL
FROM core."user" u WHERE u.email = 'admin@goreos.cl';

INSERT INTO core.notification (user_id, title, body, category, entity_type, link, read_at)
SELECT u.id,
       'SLA cumplido: rendicion aprobada',
       'La rendicion del convenio CNV-2026-005 fue aprobada dentro del plazo.',
       'sla',
       'core.rendition',
       '/datos?dominio=rendiciones',
       NOW() - INTERVAL '2 hours'
FROM core."user" u WHERE u.email = 'admin@goreos.cl';

-- Register migration
INSERT INTO core.schema_migration (filename, checksum, applied_by)
VALUES ('goreos_migration_notifications.sql', md5('notification_table_v1'), 'claude')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
