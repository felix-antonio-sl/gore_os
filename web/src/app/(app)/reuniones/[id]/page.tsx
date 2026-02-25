"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  ArrowLeft,
  Plus,
  Play,
  Square,
  Lightbulb,
  AlertTriangle,
  Clock,
  Bug,
  CheckCircle2,
} from "lucide-react";
import type { ReunionDetail, TopicItem, AutoSuggestion } from "@/types";

interface IprOption {
  id: string;
  codigo_bip: string;
  name: string;
}

interface UserOption {
  id: string;
  nombre: string;
  apellido_paterno: string;
  division_name: string | null;
}

function formatDateTime(dateStr: string | null | undefined): string {
  if (!dateStr) return "-";
  try {
    return new Intl.DateTimeFormat("es-CL", {
      weekday: "long",
      day: "2-digit",
      month: "long",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(dateStr));
  } catch {
    return dateStr;
  }
}

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "-";
  try {
    return new Intl.DateTimeFormat("es-CL", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    }).format(new Date(dateStr));
  } catch {
    return dateStr;
  }
}

function StatusBadgeReunion({ status }: { status: string }) {
  switch (status) {
    case "PROGRAMADA":
      return (
        <Badge variant="outline" className="border-blue-400 text-blue-600">
          Programada
        </Badge>
      );
    case "EN_CURSO":
      return (
        <Badge variant="default" className="bg-amber-500 animate-pulse">
          En Curso
        </Badge>
      );
    case "FINALIZADA":
      return (
        <Badge variant="default" className="bg-green-600">
          Finalizada
        </Badge>
      );
    default:
      return <Badge variant="secondary">{status}</Badge>;
  }
}

function SuggestionIcon({ type }: { type: string }) {
  switch (type) {
    case "alerta_critica":
      return <AlertTriangle className="size-4 text-red-500" />;
    case "compromiso_vencido":
      return <Clock className="size-4 text-amber-500" />;
    case "problema_abierto":
      return <Bug className="size-4 text-orange-500" />;
    default:
      return <Lightbulb className="size-4 text-blue-500" />;
  }
}

function suggestionTypeLabel(type: string): string {
  switch (type) {
    case "alerta_critica":
      return "Alerta Critica";
    case "compromiso_vencido":
      return "Compromiso Vencido";
    case "problema_abierto":
      return "Problema Abierto";
    default:
      return type;
  }
}

export default function ReunionDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const id = params.id as string;

  const [reunion, setReunion] = useState<ReunionDetail | null>(null);
  const [loading, setLoading] = useState(true);

  // Suggestions
  const [suggestions, setSuggestions] = useState<AutoSuggestion[] | null>(null);
  const [suggestionsLoading, setSuggestionsLoading] = useState(false);

  // Add topic form
  const [showTopicForm, setShowTopicForm] = useState(false);
  const [topicSubject, setTopicSubject] = useState("");
  const [topicIprId, setTopicIprId] = useState("");
  const [topicResponsibleId, setTopicResponsibleId] = useState("");
  const [topicDueDate, setTopicDueDate] = useState("");
  const [topicSubmitting, setTopicSubmitting] = useState(false);
  const [topicError, setTopicError] = useState<string | null>(null);

  // Review topic
  const [reviewingId, setReviewingId] = useState<string | null>(null);
  const [reviewDecision, setReviewDecision] = useState("");
  const [reviewSubmitting, setReviewSubmitting] = useState(false);

  // Finalizar
  const [showFinalize, setShowFinalize] = useState(false);
  const [finalizeSummary, setFinalizeSummary] = useState("");
  const [finalizeSubmitting, setFinalizeSubmitting] = useState(false);

  // Catalogs
  const [iprs, setIprs] = useState<IprOption[]>([]);
  const [users, setUsers] = useState<UserOption[]>([]);

  // Action state
  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const canManage =
    user &&
    ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION"].includes(user.role_code);

  const loadReunion = useCallback(() => {
    setLoading(true);
    api
      .get<ReunionDetail>(`/api/reuniones/${id}`)
      .then((data) => {
        setReunion(data);
        setFinalizeSummary(data.summary || "");
      })
      .catch(() => setReunion(null))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    loadReunion();
  }, [loadReunion]);

  // Load catalogs when topic form opens
  useEffect(() => {
    if (showTopicForm && iprs.length === 0) {
      api.get<IprOption[]>("/api/catalogs/iprs").then(setIprs).catch(() => {});
      api.get<UserOption[]>("/api/catalogs/users").then(setUsers).catch(() => {});
    }
  }, [showTopicForm, iprs.length]);

  const loadSuggestions = () => {
    setSuggestionsLoading(true);
    api
      .get<AutoSuggestion[]>(`/api/reuniones/${id}/preparar`)
      .then(setSuggestions)
      .catch(() => setSuggestions([]))
      .finally(() => setSuggestionsLoading(false));
  };

  const addSuggestionAsTopic = async (suggestion: AutoSuggestion) => {
    try {
      await api.post(`/api/reuniones/${id}/temas`, {
        subject: suggestion.subject,
        ipr_id: null,
      });
      loadReunion();
    } catch {
      // silently fail
    }
  };

  const handleAddTopic = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topicSubject.trim()) {
      setTopicError("El tema es requerido.");
      return;
    }

    setTopicSubmitting(true);
    setTopicError(null);
    try {
      await api.post(`/api/reuniones/${id}/temas`, {
        subject: topicSubject,
        ipr_id: topicIprId && topicIprId !== "none" ? topicIprId : null,
        responsible_id: topicResponsibleId && topicResponsibleId !== "none" ? topicResponsibleId : null,
        due_date: topicDueDate || null,
      });
      setTopicSubject("");
      setTopicIprId("");
      setTopicResponsibleId("");
      setTopicDueDate("");
      setShowTopicForm(false);
      loadReunion();
    } catch (err) {
      setTopicError(err instanceof Error ? err.message : "Error al agregar tema");
    } finally {
      setTopicSubmitting(false);
    }
  };

  const handleReviewTopic = async (topicId: string) => {
    setReviewSubmitting(true);
    try {
      await api.post(`/api/reuniones/${id}/temas/${topicId}/revisar`, {
        decision: reviewDecision || null,
        status: "TRATADO",
      });
      setReviewingId(null);
      setReviewDecision("");
      loadReunion();
    } catch {
      // silently fail
    } finally {
      setReviewSubmitting(false);
    }
  };

  const handleStart = async () => {
    setActionLoading(true);
    setActionError(null);
    try {
      await api.post(`/api/reuniones/${id}/iniciar`);
      loadReunion();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "Error al iniciar");
    } finally {
      setActionLoading(false);
    }
  };

  const handleFinalize = async () => {
    setFinalizeSubmitting(true);
    setActionError(null);
    try {
      await api.post(`/api/reuniones/${id}/finalizar`, {
        summary: finalizeSummary || null,
      });
      setShowFinalize(false);
      loadReunion();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "Error al finalizar");
    } finally {
      setFinalizeSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6 space-y-4">
        <div className="h-8 w-40 rounded bg-muted animate-pulse" />
        <div className="h-48 rounded-xl bg-muted animate-pulse" />
        <div className="h-64 rounded-xl bg-muted animate-pulse" />
      </div>
    );
  }

  if (!reunion) {
    return (
      <div className="p-6">
        <Button variant="ghost" size="sm" onClick={() => router.push("/reuniones")}>
          <ArrowLeft className="size-4 mr-1" />
          Volver
        </Button>
        <p className="mt-4 text-muted-foreground">Reunion no encontrada.</p>
      </div>
    );
  }

  const isProgramada = reunion.status === "PROGRAMADA";
  const isEnCurso = reunion.status === "EN_CURSO";
  const isFinalizada = reunion.status === "FINALIZADA";

  return (
    <div className="p-6 space-y-4">
      <Button variant="ghost" size="sm" onClick={() => router.push("/reuniones")}>
        <ArrowLeft className="size-4 mr-1" />
        Volver a Reuniones
      </Button>

      {/* Header */}
      <div className="rounded-xl border bg-card p-5">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span className="font-mono text-sm text-muted-foreground">
                Sesion #{reunion.session_number}
              </span>
              <StatusBadgeReunion status={reunion.status} />
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              {formatDateTime(reunion.scheduled_at)}
            </p>
            {reunion.location && (
              <p className="text-sm mt-0.5">
                <span className="text-muted-foreground">Ubicacion: </span>
                {reunion.location}
              </p>
            )}
            {reunion.organizer_name && (
              <p className="text-sm mt-0.5">
                <span className="text-muted-foreground">Organizador: </span>
                {reunion.organizer_name}
              </p>
            )}
          </div>
          <div className="flex gap-2">
            {isProgramada && canManage && (
              <Button onClick={handleStart} disabled={actionLoading}>
                <Play className="size-4 mr-1" />
                {actionLoading ? "Iniciando..." : "Iniciar Reunion"}
              </Button>
            )}
            {isEnCurso && canManage && (
              <Button
                variant="destructive"
                onClick={() => setShowFinalize(true)}
                disabled={actionLoading}
              >
                <Square className="size-4 mr-1" />
                Finalizar Reunion
              </Button>
            )}
          </div>
        </div>
        {reunion.summary && (
          <div className="mt-3 p-3 rounded-md bg-muted/50">
            <p className="text-xs uppercase font-medium text-muted-foreground tracking-wide mb-1">
              Resumen
            </p>
            <p className="text-sm">{reunion.summary}</p>
          </div>
        )}
        {actionError && (
          <p className="text-sm text-red-600 mt-2">{actionError}</p>
        )}
      </div>

      {/* Finalize modal */}
      {showFinalize && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Finalizar Reunion</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Resumen final</label>
              <textarea
                className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                value={finalizeSummary}
                onChange={(e) => setFinalizeSummary(e.target.value)}
                placeholder="Resumen de la reunion..."
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleFinalize} disabled={finalizeSubmitting} variant="destructive">
                {finalizeSubmitting ? "Finalizando..." : "Confirmar Finalizacion"}
              </Button>
              <Button variant="outline" onClick={() => setShowFinalize(false)}>
                Cancelar
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Preparar section (PROGRAMADA only) */}
      {isProgramada && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base flex items-center gap-2">
                <Lightbulb className="size-4" />
                Preparar Reunion
              </CardTitle>
              <Button size="sm" variant="outline" onClick={loadSuggestions} disabled={suggestionsLoading}>
                {suggestionsLoading ? "Cargando..." : "Obtener Sugerencias"}
              </Button>
            </div>
          </CardHeader>
          {suggestions && suggestions.length > 0 && (
            <CardContent className="space-y-2">
              <p className="text-xs text-muted-foreground mb-2">
                Temas sugeridos basados en alertas, compromisos y problemas activos:
              </p>
              {suggestions.map((s, i) => (
                <div
                  key={i}
                  className="flex items-start gap-3 rounded-md border p-3 hover:bg-accent/50 transition-colors"
                >
                  <SuggestionIcon type={s.type} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <Badge variant="outline" className="text-[10px]">
                        {suggestionTypeLabel(s.type)}
                      </Badge>
                      {s.ipr_codigo_bip && (
                        <span className="font-mono text-[10px] text-muted-foreground">
                          {s.ipr_codigo_bip}
                        </span>
                      )}
                    </div>
                    <p className="text-sm line-clamp-2">{s.subject}</p>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => addSuggestionAsTopic(s)}
                  >
                    <Plus className="size-3 mr-1" />
                    Agregar
                  </Button>
                </div>
              ))}
            </CardContent>
          )}
          {suggestions && suggestions.length === 0 && (
            <CardContent>
              <p className="text-sm text-muted-foreground">
                No se encontraron sugerencias automaticas. Puede agregar temas manualmente.
              </p>
            </CardContent>
          )}
        </Card>
      )}

      {/* Topics section */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">
              Temas ({reunion.topics.length})
            </CardTitle>
            {!isFinalizada && (
              <Button size="sm" onClick={() => setShowTopicForm(true)}>
                <Plus className="size-4 mr-1" />
                Agregar Tema
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {/* Add topic form */}
          {showTopicForm && (
            <form
              onSubmit={handleAddTopic}
              className="rounded-md border p-4 space-y-3 bg-muted/30"
            >
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Tema *</label>
                <Input
                  value={topicSubject}
                  onChange={(e) => setTopicSubject(e.target.value)}
                  placeholder="Describa el tema a tratar..."
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">IPR asociada</label>
                  <Select value={topicIprId} onValueChange={setTopicIprId}>
                    <SelectTrigger>
                      <SelectValue placeholder="Sin IPR" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">Sin IPR</SelectItem>
                      {iprs.map((ipr) => (
                        <SelectItem key={ipr.id} value={ipr.id}>
                          {ipr.codigo_bip} — {ipr.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Responsable</label>
                  <Select value={topicResponsibleId} onValueChange={setTopicResponsibleId}>
                    <SelectTrigger>
                      <SelectValue placeholder="Sin asignar" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">Sin asignar</SelectItem>
                      {users.map((u) => (
                        <SelectItem key={u.id} value={u.id}>
                          {u.nombre} {u.apellido_paterno}
                          {u.division_name ? ` (${u.division_name})` : ""}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Plazo</label>
                  <Input
                    type="date"
                    value={topicDueDate}
                    onChange={(e) => setTopicDueDate(e.target.value)}
                  />
                </div>
              </div>
              {topicError && (
                <p className="text-sm text-red-600">{topicError}</p>
              )}
              <div className="flex gap-2">
                <Button type="submit" size="sm" disabled={topicSubmitting}>
                  {topicSubmitting ? "Agregando..." : "Agregar"}
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={() => setShowTopicForm(false)}
                >
                  Cancelar
                </Button>
              </div>
            </form>
          )}

          {/* Topic list */}
          {reunion.topics.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4 text-center">
              No hay temas agregados. Use el boton &quot;Agregar Tema&quot; o las sugerencias automaticas.
            </p>
          ) : (
            reunion.topics.map((topic: TopicItem) => (
              <div
                key={topic.id}
                className="rounded-md border p-4 space-y-2"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className="font-mono text-xs text-muted-foreground">
                        #{topic.agreement_number}
                      </span>
                      {topic.status && (
                        <Badge
                          variant={topic.status === "TRATADO" ? "default" : "outline"}
                          className={
                            topic.status === "TRATADO"
                              ? "text-[10px] px-1.5 py-0 bg-green-600"
                              : "text-[10px] px-1.5 py-0"
                          }
                        >
                          {topic.status === "TRATADO" ? "Tratado" : topic.status}
                        </Badge>
                      )}
                      {topic.context_type && (
                        <Badge variant="outline" className="text-[10px] px-1.5 py-0">
                          {topic.context_type}
                        </Badge>
                      )}
                      {topic.ipr_codigo_bip && (
                        <span className="font-mono text-[10px] text-muted-foreground">
                          BIP: {topic.ipr_codigo_bip}
                        </span>
                      )}
                    </div>
                    <p className="text-sm font-medium">{topic.subject}</p>
                    {topic.decision && (
                      <div className="mt-1 p-2 rounded bg-green-50 border border-green-200">
                        <p className="text-xs font-medium text-green-800">Decision:</p>
                        <p className="text-sm text-green-700">{topic.decision}</p>
                      </div>
                    )}
                    <div className="flex gap-4 mt-1 text-xs text-muted-foreground">
                      {topic.responsible_name && (
                        <span>Responsable: {topic.responsible_name}</span>
                      )}
                      {topic.due_date && (
                        <span>Plazo: {formatDate(topic.due_date)}</span>
                      )}
                    </div>
                  </div>

                  {/* Review button (EN_CURSO only) */}
                  {isEnCurso && topic.status !== "TRATADO" && (
                    <div className="shrink-0">
                      {reviewingId === topic.id ? (
                        <div className="space-y-2 w-64">
                          <textarea
                            className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                            value={reviewDecision}
                            onChange={(e) => setReviewDecision(e.target.value)}
                            placeholder="Decision o acuerdo tomado..."
                          />
                          <div className="flex gap-1">
                            <Button
                              size="sm"
                              onClick={() => handleReviewTopic(topic.id)}
                              disabled={reviewSubmitting}
                            >
                              <CheckCircle2 className="size-3 mr-1" />
                              {reviewSubmitting ? "..." : "Revisar"}
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => {
                                setReviewingId(null);
                                setReviewDecision("");
                              }}
                            >
                              Cancelar
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setReviewingId(topic.id);
                            setReviewDecision(topic.decision || "");
                          }}
                        >
                          <CheckCircle2 className="size-3 mr-1" />
                          Revisar
                        </Button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
