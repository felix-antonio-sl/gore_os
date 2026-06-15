"use client";

import { ReactNode, useState } from "react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ConfirmDialog } from "@/components/confirm-dialog";

interface DrawerPanelProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  wide?: boolean;
  /** When true, closing (overlay/X/Esc) asks for confirmation to avoid losing edits. */
  isDirty?: boolean;
}

export function DrawerPanel({ open, onClose, title, children, wide, isDirty = false }: DrawerPanelProps) {
  const [confirmOpen, setConfirmOpen] = useState(false);

  const requestClose = () => {
    if (isDirty) {
      setConfirmOpen(true);
    } else {
      onClose();
    }
  };

  return (
    <>
      <Sheet open={open} onOpenChange={(isOpen) => { if (!isOpen) requestClose(); }}>
        <SheetContent side="right" className={`flex flex-col p-0 ${wide ? "sm:max-w-xl" : ""}`}>
          <SheetHeader className="px-6 py-4 border-b">
            <SheetTitle>{title}</SheetTitle>
          </SheetHeader>
          <ScrollArea className="flex-1">
            <div className="px-6 py-4">
              {children}
            </div>
          </ScrollArea>
        </SheetContent>
      </Sheet>

      <ConfirmDialog
        open={confirmOpen}
        onOpenChange={setConfirmOpen}
        title="Cambios sin guardar"
        description="Tienes cambios sin guardar — si cierras ahora se perderá lo que escribiste."
        confirmLabel="Descartar cambios"
        cancelLabel="Seguir editando"
        variant="destructive"
        onConfirm={() => {
          setConfirmOpen(false);
          onClose();
        }}
      />
    </>
  );
}
