import { useState, useEffect } from 'react';
import { trpc } from '../../trpc';
import { GoreBadge } from '@gore-os/ui/src/atoms/GoreBadge';
import { Icons } from '@gore-os/ui/src/atoms/GoreIcon';

// Types for display
interface ProblemaDisplay {
  id_problema: string;
  ipr_id: string;
  ipr_nombre: string | null;
  tipo: string;
  impacto: string;
  descripcion: string;
  fecha_registro: string | null;
}

interface CompromisoDisplay {
  id_compromiso: string;
  ipr_id: string | null;
  ipr_nombre: string | null;
  descripcion: string;
  fecha_limite: string;
  responsable_id: string;
}

interface AlertaDisplay {
  id_alerta: string;
  ipr_id: string | null;
  ipr_nombre: string | null;
  tipo: string;
  nivel: string;
  mensaje: string;
}

// Helper for impact color
const impactColor = (impacto: string) => {
  switch (impacto) {
    case 'CRITICO': return 'bg-red-500 text-white';
    case 'ALTO': return 'bg-orange-500 text-white';
    case 'MEDIO': return 'bg-yellow-500 text-black';
    default: return 'bg-gray-300 text-black';
  }
};

const nivelColor = (nivel: string) => {
  switch (nivel) {
    case 'CRITICO': return 'bg-red-600 text-white';
    case 'ALTO': return 'bg-orange-500 text-white';
    case 'ATENCION': return 'bg-yellow-400 text-black';
    default: return 'bg-blue-400 text-white';
  }
};

export function CrisisPage() {
  // Queries
  const { data: problemasAbiertos, isLoading: loadingProblemas } = trpc.problema.getAbiertos.useQuery();
  const { data: compromisosVencidos, isLoading: loadingCompromisos } = trpc.compromiso.getVencidos.useQuery();
  const { data: alertasCriticas, isLoading: loadingAlertas } = trpc.alerta.getCriticas.useQuery();
  
  // Stats
  const { data: statsProblemas } = trpc.problema.getStats.useQuery();
  const { data: statsCompromisos } = trpc.compromiso.getStats.useQuery();
  const { data: statsAlertas } = trpc.alerta.getStats.useQuery();

  const isLoading = loadingProblemas || loadingCompromisos || loadingAlertas;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-pulse text-lg text-gray-500">Cargando dashboard de crisis...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gore-brand mb-2">Panel de Crisis</h1>
        <p className="text-gray-600">Gestión de problemas, compromisos y alertas de la cartera IPR</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Problemas */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 uppercase tracking-wide">Problemas Abiertos</p>
              <p className="text-3xl font-bold text-gray-900">{statsProblemas?.abiertos || 0}</p>
            </div>
            <div className="p-3 bg-red-100 rounded-full">
              <Icons.AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
          </div>
          <p className="mt-2 text-sm text-red-600">{statsProblemas?.criticos || 0} críticos</p>
        </div>

        {/* Compromisos */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 uppercase tracking-wide">Compromisos Vencidos</p>
              <p className="text-3xl font-bold text-gray-900">{statsCompromisos?.vencidos || 0}</p>
            </div>
            <div className="p-3 bg-orange-100 rounded-full">
              <Icons.Clock className="h-6 w-6 text-orange-600" />
            </div>
          </div>
          <p className="mt-2 text-sm text-orange-600">{statsCompromisos?.pendientes || 0} pendientes total</p>
        </div>

        {/* Alertas */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 uppercase tracking-wide">Alertas Activas</p>
              <p className="text-3xl font-bold text-gray-900">{statsAlertas?.activas || 0}</p>
            </div>
            <div className="p-3 bg-yellow-100 rounded-full">
              <Icons.Bell className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
          <p className="mt-2 text-sm text-yellow-600">{statsAlertas?.criticas || 0} críticas</p>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Alertas Críticas */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 bg-red-50">
            <h2 className="text-lg font-semibold text-red-800 flex items-center gap-2">
              <Icons.AlertTriangle className="h-5 w-5" />
              Alertas Críticas
            </h2>
          </div>
          <div className="divide-y divide-gray-100">
            {alertasCriticas && alertasCriticas.length > 0 ? (
              alertasCriticas.map((alerta) => (
                <div key={alerta.id_alerta} className="px-6 py-4 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{alerta.mensaje}</p>
                      <p className="text-sm text-gray-500 mt-1">
                        IPR: {alerta.ipr_nombre || 'Sin vincular'}
                      </p>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-full ${nivelColor(alerta.nivel)}`}>
                      {alerta.nivel}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="px-6 py-8 text-center text-gray-500">
                <Icons.CheckCircle className="h-8 w-8 mx-auto text-green-500 mb-2" />
                Sin alertas críticas
              </div>
            )}
          </div>
        </section>

        {/* Compromisos Vencidos */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 bg-orange-50">
            <h2 className="text-lg font-semibold text-orange-800 flex items-center gap-2">
              <Icons.Clock className="h-5 w-5" />
              Compromisos Vencidos
            </h2>
          </div>
          <div className="divide-y divide-gray-100">
            {compromisosVencidos && compromisosVencidos.length > 0 ? (
              compromisosVencidos.slice(0, 5).map((comp) => (
                <div key={comp.id_compromiso} className="px-6 py-4 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{comp.descripcion}</p>
                      <p className="text-sm text-gray-500 mt-1">
                        IPR: {comp.ipr_nombre || 'Sin vincular'} • Vencía: {comp.fecha_limite}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="px-6 py-8 text-center text-gray-500">
                <Icons.CheckCircle className="h-8 w-8 mx-auto text-green-500 mb-2" />
                Sin compromisos vencidos
              </div>
            )}
          </div>
        </section>

        {/* Problemas Abiertos */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden lg:col-span-2">
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
            <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
              <Icons.AlertTriangle className="h-5 w-5" />
              Problemas Abiertos
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">IPR</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Impacto</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descripción</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fecha</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {problemasAbiertos && problemasAbiertos.length > 0 ? (
                  problemasAbiertos.map((prob) => (
                    <tr key={prob.id_problema} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {prob.ipr_nombre || 'Sin IPR'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{prob.tipo}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded-full ${impactColor(prob.impacto)}`}>
                          {prob.impacto}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500 max-w-md truncate">{prob.descripcion}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {prob.fecha_registro ? new Date(prob.fecha_registro).toLocaleDateString('es-CL') : '-'}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                      Sin problemas abiertos. ¡Excelente!
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
}
