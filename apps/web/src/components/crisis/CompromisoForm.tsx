import { useState } from 'react';
import { trpc } from '../../trpc';
import { Icons } from '@gore-os/ui/src/atoms/GoreIcon';

interface CompromisoFormProps {
  iprId?: string;
  iprNombre?: string;
  problemaId?: string;
  onSuccess?: () => void;
  onCancel?: () => void;
}

const TIPOS_GESTION = ['GESTION', 'DOCUMENTO', 'REUNION', 'VISITA', 'TRAMITE', 'OTRO'] as const;

export function CompromisoForm({ iprId, iprNombre, problemaId, onSuccess, onCancel }: CompromisoFormProps) {
  const [tipo, setTipo] = useState<typeof TIPOS_GESTION[number]>('GESTION');
  const [descripcion, setDescripcion] = useState('');
  const [fechaLimite, setFechaLimite] = useState('');
  const [responsableId, setResponsableId] = useState('');

  const utils = trpc.useUtils();
  const createCompromiso = trpc.compromiso.create.useMutation({
    onSuccess: () => {
      utils.compromiso.list.invalidate();
      utils.compromiso.getStats.invalidate();
      onSuccess?.();
    },
  });

  // Default fecha limite to 7 days from now
  const defaultFechaLimite = () => {
    const d = new Date();
    d.setDate(d.getDate() + 7);
    return d.toISOString().split('T')[0];
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    createCompromiso.mutate({
      iprId,
      problemaId,
      tipo,
      descripcion,
      responsableId: responsableId || '00000000-0000-0000-0000-000000000001', // TODO: real user selector
      fechaLimite: fechaLimite || defaultFechaLimite(),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="flex items-center justify-between border-b pb-4">
        <h2 className="text-xl font-semibold text-gray-900">Crear Compromiso</h2>
        {onCancel && (
          <button type="button" onClick={onCancel} className="text-gray-400 hover:text-gray-600">
            <Icons.X className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* Context Info */}
      <div className="bg-blue-50 p-4 rounded-lg space-y-1">
        {iprNombre && (
          <p className="text-sm"><span className="text-blue-600 font-medium">IPR:</span> {iprNombre}</p>
        )}
        {problemaId && (
          <p className="text-sm"><span className="text-blue-600 font-medium">Problema:</span> #{problemaId.substring(0,8)}</p>
        )}
      </div>

      {/* Tipo de Gestión */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Tipo de Gestión</label>
        <div className="grid grid-cols-3 gap-2">
          {TIPOS_GESTION.map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setTipo(t)}
              className={`px-3 py-2 text-xs font-medium rounded-lg border transition-all ${
                tipo === t
                  ? 'bg-gore-brand text-white border-gore-brand'
                  : 'bg-white text-gray-700 border-gray-200 hover:border-gray-300'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Descripción */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Descripción del Compromiso *</label>
        <textarea
          value={descripcion}
          onChange={(e) => setDescripcion(e.target.value)}
          rows={3}
          required
          minLength={5}
          placeholder="Describe la acción comprometida..."
          className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gore-brand focus:border-transparent resize-none"
        />
      </div>

      {/* Fecha Límite */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Fecha Límite *</label>
        <input
          type="date"
          value={fechaLimite}
          onChange={(e) => setFechaLimite(e.target.value)}
          required
          min={new Date().toISOString().split('T')[0]}
          className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gore-brand focus:border-transparent"
        />
      </div>

      {/* Responsable - TODO: User selector */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Responsable</label>
        <input
          type="text"
          value={responsableId}
          onChange={(e) => setResponsableId(e.target.value)}
          placeholder="UUID del responsable (TODO: selector de usuarios)"
          className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gore-brand focus:border-transparent"
        />
        <p className="text-xs text-gray-400 mt-1">Deja vacío para asignar a usuario de prueba</p>
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-4 border-t">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancelar
          </button>
        )}
        <button
          type="submit"
          disabled={createCompromiso.isPending || descripcion.length < 5}
          className="px-6 py-2 text-sm font-medium text-white bg-gore-brand rounded-lg hover:bg-gore-brand/90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {createCompromiso.isPending ? 'Guardando...' : 'Crear Compromiso'}
        </button>
      </div>

      {createCompromiso.isError && (
        <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm">
          Error: {createCompromiso.error.message}
        </div>
      )}
    </form>
  );
}
