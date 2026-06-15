/** Geometric mark inspired by GORE Ñuble logo triangles (blue/orange/green) */
export function GoreMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 48 48" className={className} aria-hidden="true">
      <polygon points="24,2 46,42 2,42" fill="#F88F3F" />
      <polygon points="12,18 34,46 2,46" fill="#FD9700" opacity="0.85" />
      <polygon points="36,18 46,46 14,46" fill="#249F4C" opacity="0.85" />
    </svg>
  );
}
