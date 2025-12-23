import * as React from "react";
import { cn } from "../lib/utils";

export interface IconProps extends React.SVGProps<SVGSVGElement> {
  size?: number | string;
}

export const GoreIcon = ({
  className,
  size = 24,
  children,
  ...props
}: IconProps) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={cn("text-gore-text", className)}
      {...props}
    >
      {children}
    </svg>
  );
};

// Iconos predefinidos comunes para GORE
export const Icons = {
  Home: (props: IconProps) => (
    <GoreIcon {...props}>
      <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
      <polyline points="9 22 9 12 15 12 15 22" />
    </GoreIcon>
  ),
  FileText: (props: IconProps) => (
    <GoreIcon {...props}>
      <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
      <polyline points="14 2 14 8 20 8" />
    </GoreIcon>
  ),
  CheckCircle: (props: IconProps) => (
    <GoreIcon {...props}>
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
    </GoreIcon>
  ),
  AlertTriangle: (props: IconProps) => (
    <GoreIcon {...props}>
      <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </GoreIcon>
  ),
};
