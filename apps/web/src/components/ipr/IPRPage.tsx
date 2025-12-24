import React, { useState } from 'react';
import { trpc } from '../../trpc';
import { IPRCard } from '@gore-os/ui/src/organisms/IPRCard';
import { GoreBadge } from '@gore-os/ui/src/atoms/GoreBadge';
import { Icons } from '@gore-os/ui/src/atoms/GoreIcon';
import { IPRForm } from './IPRForm';

export const IPRPage = () => {
  const { data: iprs, isLoading, error } = trpc.ipr.list.useQuery();
  const [isCreateOpen, setCreateOpen] = useState(false);

  if (isLoading) return <div className="p-8">Cargando cartera IPR...</div>;
  if (error) return <div className="p-8 text-red-500">Error al cargar: {error.message}</div>;

  return (
    <div className="container mx-auto py-8">
      {/* HEADER */}
      <div className="mb-8 flex items-center justify-between">
        <div>
           <h1 className="text-3xl font-bold tracking-tight text-gore-brand">Cartera de Inversión (M1)</h1>
           <p className="text-muted-foreground">Gestión del ciclo de vida de Iniciativas de Inversión Regional</p>
        </div>
        <button 
          className="inline-flex items-center justify-center rounded-md bg-gore-brand px-4 py-2 text-sm font-medium text-white hover:bg-gore-brand/90 focus:outline-none focus:ring-2 focus:ring-gore-brand focus:ring-offset-2"
          onClick={() => setCreateOpen(true)}
        >
          <Icons.Plus className="mr-2 h-4 w-4" />
          Nueva IPR
        </button>
      </div>

      {/* LIST GRID */}
      {!iprs || iprs.length === 0 ? (
        <div className="rounded-lg border border-dashed p-12 text-center">
          <Icons.Folder className="mx-auto h-12 w-12 text-gray-300" />
          <h3 className="mt-4 text-lg font-medium">No hay iniciativas</h3>
          <p className="text-gray-500">Comienza creando una nueva IPR para visualizarla aquí.</p>
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {iprs.map((ipr) => (
            <IPRCard
              key={ipr.id_ipr}
              code={ipr.codigo_bip}
              name={ipr.nombre}
              amount={parseFloat(ipr.monto_total)}
              stage={ipr.etapa_actual}
              location={ipr.comuna_nombre || 'Sin Comuna'} 
              status={mapStatus(ipr.estado_ciclo)}
              onClick={() => console.log("Click IPR", ipr.id_ipr)}
            />
          ))}
        </div>
      )}

      {/* SIMPLE MODAL (In a real app, use Dialog/Modal primitive) */}
      {isCreateOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-lg rounded-lg bg-white p-6 shadow-xl">
             <IPRForm 
               onSuccess={() => setCreateOpen(false)} 
               onCancel={() => setCreateOpen(false)}
             />
          </div>
        </div>
      )}
    </div>
  );
};

function mapStatus(ciclo: string): "active" | "alert" | "finished" {
  if (ciclo === 'CIERRE') return 'finished';
  if (ciclo === 'EJECUCION') return 'active';
  return 'active'; // Default
}
