-- model/model_goreos/sql/goreos_seed_etl_phase2.sql
-- Phase 2 ETL seed: document_channel scheme
-- Idempotent: ON CONFLICT DO NOTHING

INSERT INTO ref.category (scheme, code, label) VALUES
  ('document_channel', 'EMAIL',      'Email'),
  ('document_channel', 'PAPEL',      'Papel físico'),
  ('document_channel', 'DOCDIGITAL', 'Documento digital'),
  ('document_channel', 'OTRO',       'Otro')
ON CONFLICT (scheme, code) DO NOTHING;
