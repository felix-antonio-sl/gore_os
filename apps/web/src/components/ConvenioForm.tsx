import { useState } from 'react';
import { trpc } from '../trpc';
import { CurrencyInput, GoreBadge } from '@gore-os/ui';

interface ConvenioFormProps {
  onSuccess?: () => void;
}

export function ConvenioForm({ onSuccess }: ConvenioFormProps) {
  const utils = trpc.useUtils();
  const createMutation = trpc.convenio.create.useMutation({
    onSuccess: () => {
      utils.convenio.list.invalidate();
      onSuccess?.();
      setForm({ nombre: '', ministerio: '', regionId: '', montoTotal: 0, fechaFirma: '', vigenciaAnios: 1 });
    },
  });

  const [form, setForm] = useState({
    nombre: '',
    ministerio: '',
    regionId: '',
    montoTotal: 0,
    fechaFirma: '',
    vigenciaAnios: 1,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(form);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-bold text-gore-brand border-b pb-2">Nuevo Convenio</h2>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Nombre del Convenio</label>
          <input
            type="text"
            value={form.nombre}
            onChange={(e) => setForm({ ...form, nombre: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-gore-brand"
            placeholder="Ej: Convenio MOP - Caminos Rurales"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Ministerio</label>
          <input
            type="text"
            value={form.ministerio}
            onChange={(e) => setForm({ ...form, ministerio: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-gore-brand"
            placeholder="Ej: MOP"
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Región (UUID)</label>
          <input
            type="text"
            value={form.regionId}
            onChange={(e) => setForm({ ...form, regionId: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-gore-brand"
            placeholder="550e8400-e29b-..."
            required
          />
        </div>
        <CurrencyInput
          label="Monto Total"
          onValueChange={(v) => setForm({ ...form, montoTotal: v })}
        />
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Vigencia (años)</label>
          <input
            type="number"
            value={form.vigenciaAnios}
            onChange={(e) => setForm({ ...form, vigenciaAnios: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-gore-brand"
            min={1}
            required
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Fecha de Firma</label>
        <input
          type="date"
          value={form.fechaFirma}
          onChange={(e) => setForm({ ...form, fechaFirma: e.target.value })}
          className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-gore-brand"
          required
        />
      </div>

      <button
        type="submit"
        disabled={createMutation.isPending}
        className="w-full bg-gore-brand text-white py-2 px-4 rounded-lg hover:bg-gore-brand/90 disabled:opacity-50 transition-colors"
      >
        {createMutation.isPending ? 'Guardando...' : 'Crear Convenio'}
      </button>

      {createMutation.isError && (
        <GoreBadge variant="destructive">Error: {createMutation.error.message}</GoreBadge>
      )}
    </form>
  );
}
