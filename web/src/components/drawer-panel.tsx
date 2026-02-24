"use client";

import { ReactNode } from "react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";

interface DrawerPanelProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
}

export function DrawerPanel({ open, onClose, title, children }: DrawerPanelProps) {
  return (
    <Sheet open={open} onOpenChange={(isOpen) => { if (!isOpen) onClose(); }}>
      <SheetContent side="right" className="w-[400px] sm:w-[400px] flex flex-col p-0">
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
  );
}
