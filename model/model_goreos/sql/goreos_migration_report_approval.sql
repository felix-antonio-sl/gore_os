-- Migration: Add EN_REVISION status for DGI report approval workflow
INSERT INTO ref.category (scheme, code, label)
VALUES ('dgi_report_status', 'EN_REVISION', 'En Revisión')
ON CONFLICT (scheme, code) DO NOTHING;
