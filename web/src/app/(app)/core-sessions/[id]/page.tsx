"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter, usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  ThumbsUp,
  ThumbsDown,
  MinusCircle,
  Play,
  Square,
  Plus,
  CheckCircle2,
  XCircle,
  Clock,
  Users,
} from "lucide-react";
import { formatDateTime } from "@/lib/format";
import { Breadcrumb } from "@/components/breadcrumb";
import { buildBreadcrumbs } from "@/lib/breadcrumbs";
import type { CoreSessionDetail, TopicWithVotes, MemberAttendance } from "@/types";

function StatusBadge({ status }: { status: string }) {
  switch (status) {
    case "PROGRAMADA":
      return <Badge variant="outline" className="border-blue-400 text-blue-600">Programada</Badge>;
    case "EN_CURSO":
      return <Badge variant="default" className="bg-amber-500 animate-pulse">En Curso</Badge>;
    case "FINALIZADA":
      return <Badge variant="default" className="bg-green-600">Finalizada</Badge>;
    default:
      return <Badge variant="secondary">{status}</Badge>;
  }
}

function VoteResultBadge({ result }: { result: string }) {
  switch (result) {
    case "APROBADO":
      return (
        <Badge className="bg-green-600 text-white">
          <CheckCircle2 className="size-3 mr-1" />Aprobado
        </Badge>
      );
    case "RECHAZADO":
      return (
        <Badge className="bg-red-600 text-white">
          <XCircle className="size-3 mr-1" />Rechazado
        </Badge>
      );
    default:
      return (
        <Badge variant="outline" className="border-amber-400 text-amber-600">
          <Clock className="size-3 mr-1" />Pendiente
        </Badge>
      );
  }
}

const MANAGER_ROLES = ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "SECRETARIO_EJECUTIVO"];

export default function CoreSessionDetailPage() {
  const params = useParams();
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();
  const sessionId = params.id as string;

  const [session, setSession] = useState<CoreSessionDetail | null>(null);
  const [members, setMembers] = useState<MemberAttendance[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Add topic form
  const [showTopicForm, setShowTopicForm] = useState(false);
  const [topicSubject, setTopicSubject] = useState("");
  const [topicQuorum, setTopicQuorum] = useState("SIMPLE");

  const isManager = user && MANAGER_ROLES.includes(user.role_code);
  const isConsejero = user?.role_code === "CONSEJERO_REGIONAL";

  const fetchData = useCallback(async () => {
    try {
      const [s, m] = await Promise.all([
        api.get<CoreSessionDetail>(`/api/core-sessions/${sessionId}`),
        api.get<MemberAttendance[]>(`/api/core-sessions/${sessionId}/miembros`),
      ]);
      setSession(s);
      setMembers(m);
    } catch {
      setError("Error al cargar la sesion");
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleStart = async () => {
    setActionLoading(true);
    try {
      await api.post(`/api/core-sessions/${sessionId}/iniciar`, {});
      await fetchData();
    } catch (err) {
      setError(String(err));
    } finally {
      setActionLoading(false);
    }
  };

  const handleFinish = async () => {
    setActionLoading(true);
    try {
      await api.post(`/api/core-sessions/${sessionId}/finalizar`, {});
      await fetchData();
    } catch (err) {
      setError(String(err));
    } finally {
      setActionLoading(false);
    }
  };

  const handleAddTopic = async () => {
    if (!topicSubject.trim()) return;
    setActionLoading(true);
    try {
      await api.post(`/api/core-sessions/${sessionId}/temas`, {
        subject: topicSubject,
        quorum_type: topicQuorum,
      });
      setTopicSubject("");
      setShowTopicForm(false);
      await fetchData();
    } catch (err) {
      setError(String(err));
    } finally {
      setActionLoading(false);
    }
  };

  const handleVote = async (temaId: string, vote: string) => {
    setActionLoading(true);
    try {
      await api.post(`/api/core-sessions/${sessionId}/temas/${temaId}/votar`, { vote });
      await fetchData();
    } catch (err) {
      setError(String(err));
    } finally {
      setActionLoading(false);
    }
  };

  if (isLoading) {
    return <div className="p-6"><p className="text-muted-foreground">Cargando...</p></div>;
  }

  if (!session) {
    return <div className="p-6"><p className="text-red-500">{error || "Sesión no encontrada"}</p></div>;
  }

  return (
    <div className="p-6 space-y-6 max-w-4xl">
      <Breadcrumb items={buildBreadcrumbs(pathname, "Sesión #" + session?.session_number)} />
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">
              Sesión {session.session_type === "EXTRAORDINARIA" ? "Extraordinaria" : "Ordinaria"} #{session.session_number}
            </h1>
            <StatusBadge status={session.status} />
          </div>
          <p className="text-muted-foreground text-sm mt-1">
            {formatDateTime(session.scheduled_at)}
            {session.location && ` — ${session.location}`}
          </p>
          <div className="flex items-center gap-2 mt-2">
            <Users className="size-4 text-muted-foreground" />
            <span className="text-sm">
              Miembros: {session.members_present}/{session.members_total}
              {session.quorum_reached !== null && (
                session.quorum_reached
                  ? <span className="text-green-600 ml-1">(Quorum alcanzado)</span>
                  : <span className="text-red-600 ml-1">(Sin quorum)</span>
              )}
            </span>
          </div>
        </div>
        <div className="flex gap-2">
          {isManager && session.status === "PROGRAMADA" && (
            <Button onClick={handleStart} disabled={actionLoading}>
              <Play className="size-4 mr-1" />Iniciar
            </Button>
          )}
          {isManager && session.status === "EN_CURSO" && (
            <Button variant="destructive" onClick={handleFinish} disabled={actionLoading}>
              <Square className="size-4 mr-1" />Finalizar
            </Button>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700">
          {error}
          <Button variant="ghost" size="sm" className="ml-2" onClick={() => setError(null)}>Cerrar</Button>
        </div>
      )}

      {/* Topics */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Temas para Votación ({session.topics.length})</CardTitle>
            {isManager && session.status !== "FINALIZADA" && (
              <Button size="sm" variant="outline" onClick={() => setShowTopicForm(!showTopicForm)}>
                <Plus className="size-4 mr-1" />{showTopicForm ? "Cancelar" : "Agregar Tema"}
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {showTopicForm && (
            <div className="border rounded-md p-4 space-y-3 bg-muted/30">
              <div className="space-y-2">
                <label className="text-sm font-medium">Tema</label>
                <Input
                  value={topicSubject}
                  onChange={(e) => setTopicSubject(e.target.value)}
                  placeholder="Descripción del tema a votar..."
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Tipo de Quórum</label>
                <Select value={topicQuorum} onValueChange={setTopicQuorum}>
                  <SelectTrigger className="w-[250px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="SIMPLE">Mayoría Simple (9/16)</SelectItem>
                    <SelectItem value="CALIFICADA">Mayoría Calificada (11/16)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button size="sm" onClick={handleAddTopic} disabled={actionLoading || !topicSubject.trim()}>
                Agregar
              </Button>
            </div>
          )}

          {session.topics.length === 0 && (
            <p className="text-sm text-muted-foreground text-center py-4">
              No hay temas registrados
            </p>
          )}

          {session.topics.map((topic: TopicWithVotes) => (
            <TopicCard
              key={topic.id}
              topic={topic}
              sessionStatus={session.status}
              isConsejero={!!isConsejero}
              onVote={handleVote}
              actionLoading={actionLoading}
              router={router}
            />
          ))}
        </CardContent>
      </Card>

      {/* Members */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">
            Miembros del Consejo ({members.filter(m => m.has_voted_in_session).length}/{members.length} han votado)
          </CardTitle>
        </CardHeader>
        <CardContent>
          {members.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              No hay miembros registrados en el Consejo
            </p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {members.map((m) => (
                <div key={m.member_id} className="flex items-center gap-2 py-1.5 px-2 rounded-md hover:bg-muted/50">
                  <div className={`size-2 rounded-full ${m.has_voted_in_session ? "bg-green-500" : "bg-gray-300"}`} />
                  <span className="text-sm font-medium">{m.person_name}</span>
                  {m.role_in_committee && (
                    <span className="text-xs text-muted-foreground">({m.role_in_committee})</span>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function TopicCard({
  topic,
  sessionStatus,
  isConsejero,
  onVote,
  actionLoading,
  router,
}: {
  topic: TopicWithVotes;
  sessionStatus: string;
  isConsejero: boolean;
  onVote: (temaId: string, vote: string) => void;
  actionLoading: boolean;
  router: ReturnType<typeof useRouter>;
}) {
  const canVote = isConsejero && sessionStatus === "EN_CURSO";

  return (
    <div className="border rounded-lg p-4 space-y-3">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs text-muted-foreground">#{topic.agreement_number}</span>
            <span className="font-medium text-sm">{topic.subject}</span>
          </div>
          {topic.ipr_codigo_bip && (
            <button
              className="text-xs text-blue-600 hover:underline"
              onClick={() => router.push(`/ipr/${topic.ipr_id}`)}
            >
              IPR {topic.ipr_codigo_bip}
            </button>
          )}
          <div className="text-xs text-muted-foreground">
            {topic.quorum_type === "CALIFICADA" ? "Mayoría Calificada (11/16)" : "Mayoría Simple (9/16)"}
          </div>
        </div>
        <VoteResultBadge result={topic.result} />
      </div>

      <Separator />

      {/* Vote counts */}
      <div className="flex items-center gap-4 text-sm">
        <div className="flex items-center gap-1 text-green-600">
          <ThumbsUp className="size-4" />
          <span className="font-medium">{topic.votes_favor}</span>
          <span className="text-muted-foreground">a favor</span>
        </div>
        <div className="flex items-center gap-1 text-red-600">
          <ThumbsDown className="size-4" />
          <span className="font-medium">{topic.votes_contra}</span>
          <span className="text-muted-foreground">en contra</span>
        </div>
        <div className="flex items-center gap-1 text-gray-500">
          <MinusCircle className="size-4" />
          <span className="font-medium">{topic.votes_abstencion}</span>
          <span className="text-muted-foreground">abstenciones</span>
        </div>
        <span className="text-xs text-muted-foreground ml-auto">
          {topic.votes_total}/{topic.required_votes} requeridos
        </span>
      </div>

      {/* Vote buttons for consejeros */}
      {canVote && (
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            className="text-green-600 border-green-300 hover:bg-green-50"
            onClick={() => onVote(topic.id, "A_FAVOR")}
            disabled={actionLoading}
          >
            <ThumbsUp className="size-3 mr-1" />A Favor
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="text-red-600 border-red-300 hover:bg-red-50"
            onClick={() => onVote(topic.id, "EN_CONTRA")}
            disabled={actionLoading}
          >
            <ThumbsDown className="size-3 mr-1" />En Contra
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="text-gray-500 border-gray-300 hover:bg-gray-50"
            onClick={() => onVote(topic.id, "ABSTENCION")}
            disabled={actionLoading}
          >
            <MinusCircle className="size-3 mr-1" />Abstención
          </Button>
        </div>
      )}
    </div>
  );
}
