"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { DataTable, type Column } from "@/components/data-table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

type RecordRow = Record<string, unknown>;
type Section = { key: string; label: string; fields: [string, string][] };
const ATTRIBUTE_LABELS: Record<string, string> = {
  rate_mdsf: "Resultado MDSF", etapa_bip: "Etapa BIP", sector: "Sector",
  categoria_c33: "Categoría C33", vida_util_residual: "Vida útil residual",
  informe_tecnico_favorable: "Informe técnico favorable", cofinanciamiento_anf: "Cofinanciamiento ANF",
  tipo_fril: "Tipo FRIL", cumple_norma_5k_utm: "Cumplimiento 5.000 UTM", res_subdere: "Resolución SUBDERE",
  plazo_licitacion_dias: "Plazo de licitación (días)", fase_eval_central: "Fase de evaluación central",
  rate_ses: "Resultado SES", gasto_admin_max: "Gasto administrativo máximo", eje_fomento: "Eje de fomento",
  nivel_trl: "Nivel TRL", innovacion_ctci: "Innovación CTCI", fondo_tematico: "Fondo temático",
  puntaje_evaluacion: "Puntaje de evaluación", asignacion_directa: "Asignación directa",
};
const SECTIONS: Section[] = [
  { key: "track-info", label: "Mecanismo y atributos registrados", fields: [["attribute", "Atributo"], ["value", "Valor registrado"]] },
  { key: "resoluciones", label: "Resoluciones vinculadas", fields: [["act_number", "Número"], ["subject", "Materia"], ["state", "Estado"], ["act_type_label", "Tipo"], ["issued_at", "Fecha"]] },
  { key: "historial", label: "Historial de estados", fields: [["changed_at", "Fecha"], ["previous_state", "Estado anterior"], ["new_state", "Estado registrado"], ["changed_by_name", "Autor"], ["comment", "Comentario"]] },
  { key: "cdps", label: "CDP registrados", fields: [["commitment_number", "CDP"], ["amount", "Monto"], ["issued_at", "Emisión"], ["expires_at", "Vencimiento"], ["status_label", "Estado"]] },
  { key: "avances", label: "Avances", fields: [["report_number", "Informe"], ["report_date", "Fecha"], ["physical_progress", "Avance físico"], ["financial_progress", "Avance financiero"], ["description", "Descripción"], ["issues_detected", "Problemas"], ["reported_by_name", "Autor"]] },
  { key: "partes", label: "Organizaciones y partes", fields: [["organization_name", "Organización"], ["role_label", "Rol"], ["is_primary", "Principal"], ["valid_from", "Desde"], ["valid_to", "Hasta"], ["responsibility_description", "Responsabilidad"]] },
  { key: "territorio", label: "Territorio", fields: [["territory_name", "Territorio"], ["impact_type_label", "Impacto"], ["is_primary", "Principal"]] },
  { key: "hitos", label: "Hitos", fields: [["milestone_type_label", "Tipo"], ["planned_date", "Fecha prevista"], ["actual_date", "Fecha registrada"], ["description", "Descripción"], ["completed_by_name", "Responsable"], ["verification_notes", "Verificación"]] },
  { key: "evaluaciones", label: "Evaluaciones", fields: [["evaluator_type", "Tipo"], ["evaluator_org_name", "Organización"], ["evaluator_name", "Evaluador"], ["assigned_at", "Asignación"], ["completed_at", "Finalización"], ["result_label", "Resultado"], ["numeric_score", "Puntaje"], ["rank_position", "Posición"], ["rank_total", "Total"], ["convocatoria_code", "Convocatoria"], ["observations", "Observaciones"]] },
  { key: "admisibilidad", label: "Admisibilidad", fields: [["code", "Código"], ["label", "Antecedente"], ["verified", "Verificado"], ["verified_at", "Fecha"], ["verified_by", "Autor"], ["notes", "Notas"]] },
  { key: "certificacion-tecnica", label: "Certificación técnica C33", fields: [["categoria_c33", "Categoría"], ["certifier_org", "Certificador"], ["requested_at", "Solicitud"], ["resolved_at", "Resolución"], ["informe_tecnico_favorable", "Favorable"], ["document_reference", "Documento"], ["notes", "Notas"]] },
  { key: "parentesco", label: "Declaraciones de parentesco", fields: [["person_name", "Declarante"], ["declaration_type", "Declaración"], ["declares_no_conflict", "Sin conflicto declarado"], ["related_authority_name", "Autoridad relacionada"], ["relationship_type", "Relación"], ["declared_at", "Declaración"], ["validated_at", "Validación"]] },
  { key: "modificaciones", label: "Modificaciones registradas", fields: [["code", "Código"], ["modification_type_label", "Tipo"], ["status_label", "Estado"], ["description", "Descripción"], ["justification", "Fundamento"], ["old_value", "Valor anterior"], ["new_value", "Valor registrado"], ["requested_by_name", "Solicitante"], ["approved_at", "Aprobación"]] },
  { key: "cierre", label: "Cierre registrado", fields: [["closure_date", "Fecha"], ["closure_report", "Informe"], ["physical_completion", "Avance físico"], ["financial_completion", "Avance financiero"], ["final_amount", "Monto final"], ["signed_by_name", "Firmante"], ["signed_at", "Firma"]] },
  { key: "evaluacion-expost", label: "Evaluaciones posteriores", fields: [["evaluation_date", "Fecha"], ["evaluator_name", "Evaluador"], ["eval_type_label", "Tipo"], ["rating_label", "Valoración"], ["findings", "Hallazgos"], ["recommendations", "Recomendaciones"], ["lessons_learned", "Aprendizajes"]] },
];

function cell(value: unknown) {
  if (value == null || value === "") return <span className="text-muted-foreground">—</span>;
  if (typeof value === "boolean") return value ? "Sí" : "No";
  if (typeof value === "object") return "—";
  return <span className="whitespace-pre-wrap break-words">{String(value)}</span>;
}

function Records({ iprId, section }: { iprId: string; section: Section }) {
  const [rows, setRows] = useState<RecordRow[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let active = true;
    queueMicrotask(() => { if (active) { setLoading(true); setError(null); } });
    api.get<RecordRow[] | RecordRow | null>(section.key === "resoluciones" ? `/api/actos?ipr_id=${iprId}&page=${page}&page_size=50` : `/api/ipr/${iprId}/${section.key}`)
      .then((data) => {
        if (!active) return;
        const records = section.key === "track-info" && data && !Array.isArray(data)
          ? Object.entries((data.mechanism_attrs ?? {}) as RecordRow).map(([attribute, value]) => ({ attribute: ATTRIBUTE_LABELS[attribute] ?? attribute, value }))
          : Array.isArray(data) ? data : data && Array.isArray(data.items) ? data.items as RecordRow[] : data ? [data] : [];
        setRows(records);
        const paginated = data && !Array.isArray(data) && Array.isArray(data.items) ? data : null;
        setTotal(paginated ? Number(paginated.total ?? records.length) : records.length);
        setTotalPages(paginated ? Number(paginated.total_pages ?? 1) : 1);
      })
      .catch((err) => { if (active) setError(err instanceof Error ? err.message : "No se pudieron consultar los antecedentes."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [iprId, section.key, page]);
  const columns: Column[] = section.fields.map(([key, label]) => ({ key, label, render: cell }));
  return <DataTable columns={columns} data={rows} page={page} totalPages={totalPages} total={total}
    onPageChange={setPage} isLoading={loading} error={error} emptyTitle="Sin antecedentes registrados" />;
}

export function TabAntecedentes({ iprId, initialSection }: { iprId: string; initialSection?: string }) {
  const [key, setKey] = useState(() => SECTIONS.find((section) => section.key === initialSection)?.key ?? "historial");
  const section = SECTIONS.find((item) => item.key === key) ?? SECTIONS[0];
  return (
    <section className="space-y-4">
      <div className="space-y-2">
        <h2 className="font-medium">Antecedentes del expediente</h2>
        <p className="text-sm text-muted-foreground">Registros disponibles para consulta.</p>
        <Select value={key} onValueChange={setKey}>
          <SelectTrigger aria-label="Tipo de antecedente" className="w-full sm:w-80"><SelectValue /></SelectTrigger>
          <SelectContent>{SECTIONS.map((item) => <SelectItem key={item.key} value={item.key}>{item.label}</SelectItem>)}</SelectContent>
        </Select>
      </div>
      <Records key={`${iprId}/${key}`} iprId={iprId} section={section} />
    </section>
  );
}
