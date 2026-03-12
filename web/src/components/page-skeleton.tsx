interface PageSkeletonProps {
  variant?: "list" | "detail" | "dashboard" | "create" | "admin";
}

export function PageSkeleton({ variant = "list" }: PageSkeletonProps) {
  if (variant === "dashboard") {
    return (
      <div className="p-6 space-y-4">
        <div className="h-8 w-48 rounded bg-muted animate-pulse" />
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-24 rounded-xl bg-muted animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (variant === "detail") {
    return (
      <div className="p-6 space-y-4">
        <div className="h-5 w-32 rounded bg-muted animate-pulse" />
        <div className="h-8 w-64 rounded bg-muted animate-pulse" />
        <div className="h-40 rounded-xl bg-muted animate-pulse" />
        <div className="h-64 rounded-xl bg-muted animate-pulse" />
      </div>
    );
  }

  if (variant === "create") {
    return (
      <div className="p-6 space-y-4 max-w-2xl">
        <div className="h-5 w-32 rounded bg-muted animate-pulse" />
        <div className="h-8 w-48 rounded bg-muted animate-pulse" />
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-10 rounded bg-muted animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  // list / admin
  return (
    <div className="p-6 space-y-4">
      <div className="flex justify-between">
        <div className="h-8 w-48 rounded bg-muted animate-pulse" />
        <div className="h-9 w-32 rounded bg-muted animate-pulse" />
      </div>
      <div className="h-10 rounded bg-muted animate-pulse" />
      <div className="space-y-2">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-12 rounded bg-muted animate-pulse" />
        ))}
      </div>
    </div>
  );
}
