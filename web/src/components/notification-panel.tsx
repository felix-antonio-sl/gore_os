"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Bell,
  CheckCheck,
  Clock,
  AlertTriangle,
  ArrowUp,
  FileSignature,
  Receipt,
  ListChecks,
  Settings,
  Trash2,
  BellOff,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { ScrollArea } from "@/components/ui/scroll-area";
import { api } from "@/lib/api";
import { formatRelativeTime } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { NotificationItem, NotificationUnreadCount, PaginatedResponse } from "@/types";

const POLL_INTERVAL_MS = 60_000;

const CATEGORY_CONFIG: Record<
  string,
  { icon: typeof Bell; color: string; label: string }
> = {
  alerta: {
    icon: AlertTriangle,
    color: "text-amber-500",
    label: "Alerta",
  },
  sla: {
    icon: Clock,
    color: "text-red-500",
    label: "SLA",
  },
  escalamiento: {
    icon: ArrowUp,
    color: "text-orange-500",
    label: "Escalamiento",
  },
  compromiso: {
    icon: ListChecks,
    color: "text-blue-500",
    label: "Compromiso",
  },
  rendicion: {
    icon: Receipt,
    color: "text-violet-500",
    label: "Rendicion",
  },
  firma: {
    icon: FileSignature,
    color: "text-emerald-500",
    label: "Firma",
  },
  sistema: {
    icon: Settings,
    color: "text-muted-foreground",
    label: "Sistema",
  },
};

function getCategoryConfig(category: string) {
  return CATEGORY_CONFIG[category] ?? CATEGORY_CONFIG.sistema;
}

export function NotificationPanel() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(false);

  // Poll unread count
  const fetchUnreadCount = useCallback(() => {
    api
      .get<NotificationUnreadCount>("/api/notifications/unread-count")
      .then((data) => setUnreadCount(data.count))
      .catch(() => { /* silenciar errores de red */ });
  }, []);

  useEffect(() => {
    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchUnreadCount]);

  // Fetch notifications when panel opens
  const fetchNotifications = useCallback(() => {
    setLoading(true);
    api
      .get<PaginatedResponse<NotificationItem>>(
        "/api/notifications?page_size=20"
      )
      .then((data) => setNotifications(data.items))
      .catch(() => { /* silenciar */ })
      .finally(() => setLoading(false));
  }, []);

  const handleOpenChange = (nextOpen: boolean) => {
    setOpen(nextOpen);
    if (nextOpen) fetchNotifications();
  };

  // Mark single as read and navigate
  const handleClick = async (n: NotificationItem) => {
    if (!n.read_at) {
      try {
        await api.patch(`/api/notifications/${n.id}/read`, {});
        setNotifications((prev) =>
          prev.map((item) =>
            item.id === n.id
              ? { ...item, read_at: new Date().toISOString() }
              : item
          )
        );
        setUnreadCount((c) => Math.max(0, c - 1));
      } catch { /* ignore */ }
    }
    setOpen(false);
    if (n.link) {
      router.push(n.link);
    }
  };

  // Mark all as read
  const handleMarkAllRead = async () => {
    try {
      await api.post("/api/notifications/mark-all-read");
      setNotifications((prev) =>
        prev.map((item) => ({
          ...item,
          read_at: item.read_at ?? new Date().toISOString(),
        }))
      );
      setUnreadCount(0);
    } catch { /* ignore */ }
  };

  // Soft delete
  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      await api.delete(`/api/notifications/${id}`);
      setNotifications((prev) => prev.filter((item) => item.id !== id));
      // Refresh count
      fetchUnreadCount();
    } catch { /* ignore */ }
  };

  return (
    <Popover open={open} onOpenChange={handleOpenChange}>
      <PopoverTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="relative h-8 w-8"
          aria-label="Notificaciones"
        >
          <Bell className="size-4" />
          {unreadCount > 0 && (
            <Badge className="absolute -top-0.5 -right-0.5 h-4 min-w-4 px-1 text-[10px] bg-red-500 hover:bg-red-500 text-white border-0">
              {unreadCount > 99 ? "99+" : unreadCount}
            </Badge>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-96 p-0">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b">
          <div>
            <p className="text-sm font-semibold">Notificaciones</p>
            {unreadCount > 0 && (
              <p className="text-xs text-muted-foreground">
                {unreadCount} sin leer
              </p>
            )}
          </div>
          {unreadCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-xs gap-1.5"
              onClick={handleMarkAllRead}
            >
              <CheckCheck className="size-3.5" />
              Marcar todo como leido
            </Button>
          )}
        </div>

        {/* List */}
        <ScrollArea className="max-h-[400px]">
          {loading && notifications.length === 0 ? (
            <div className="py-8 text-center">
              <p className="text-xs text-muted-foreground">Cargando...</p>
            </div>
          ) : notifications.length === 0 ? (
            <div className="flex flex-col items-center gap-2 py-10 text-muted-foreground">
              <BellOff className="size-8 stroke-1" />
              <p className="text-sm font-medium">Sin notificaciones</p>
              <p className="text-xs">Cuando haya novedades, apareceran aqui.</p>
            </div>
          ) : (
            notifications.map((n) => {
              const config = getCategoryConfig(n.category);
              const Icon = config.icon;
              const isUnread = !n.read_at;

              return (
                <div
                  key={n.id}
                  role="button"
                  tabIndex={0}
                  className={cn(
                    "flex items-start gap-3 px-4 py-3 border-b last:border-0 cursor-pointer transition-colors",
                    "hover:bg-muted/50 focus:outline-none focus:bg-muted/50",
                    isUnread && "bg-primary/5"
                  )}
                  onClick={() => handleClick(n)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      handleClick(n);
                    }
                  }}
                >
                  {/* Category icon */}
                  <div className="mt-0.5 shrink-0">
                    <Icon className={cn("size-4", config.color)} />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <p
                        className={cn(
                          "text-xs leading-snug",
                          isUnread ? "font-semibold" : "font-medium"
                        )}
                      >
                        {n.title}
                      </p>
                      {isUnread && (
                        <span className="mt-1 shrink-0 size-2 rounded-full bg-primary" />
                      )}
                    </div>
                    {n.body && (
                      <p className="text-[11px] text-muted-foreground mt-0.5 line-clamp-2">
                        {n.body}
                      </p>
                    )}
                    <p className="text-[10px] text-muted-foreground mt-1">
                      {config.label} · {formatRelativeTime(n.created_at)}
                    </p>
                  </div>

                  {/* Delete button */}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 shrink-0 opacity-0 group-hover:opacity-100 hover:opacity-100 focus:opacity-100 text-muted-foreground hover:text-destructive"
                    onClick={(e) => handleDelete(e, n.id)}
                    aria-label="Eliminar notificacion"
                  >
                    <Trash2 className="size-3" />
                  </Button>
                </div>
              );
            })
          )}
        </ScrollArea>
      </PopoverContent>
    </Popover>
  );
}
