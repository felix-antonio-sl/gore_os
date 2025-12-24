import { useState } from 'react';
import { trpc } from '../../trpc';
import { Icons } from '@gore-os/ui/src/atoms/GoreIcon';

interface ProblemaFormProps {
  iprId?: string;
  iprNombre?: string;
  onSuccess?: () => void;
  onCancel?: () => void;
}

const TIPOS = ['TECNICO', 'FINANCIERO', 'ADMINISTRATIVO', 'LEGAL', 'OTRO'] as const;
const IMPACTOS = ['BAJO', 'MEDIO', 'ALTO', 'CRITICO'] as const;

export function ProblemaForm({ iprId, iprNombre, onSuccess, onCancel }: ProblemaFormProps) {
  const [tipo, setTipo] = useState<typeof TIPOS[number]>('TECNICO');
  const [impacto, setImpacto] = useState<typeof IMPACTOS[number]>('MEDIO');
  const [descripcion, setDescripcion] = useState('');
  const [solucionPropuesta, setSolucionPropuesta] = useState('');

  const utils = trpc.useUtils();
  const createProblema = trpc.problema.create.useMutation({
    onSuccess: () => {
      utils.problema.list.invalidate();
      utils.problema.getStats.invalidate();
      onSuccess?.();
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!iprId) return;
    
    createProblema.mutate({
      iprId,
      tipo,
      impacto,
      descripcion,
      solucionPropuesta: solucionPropuesta || undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="flex items-center justify-between border-b pb-4">
        <h2 className="text-xl font-semibold text-gray-900">Registrar Problema</h2>
        {onCancel && (
          <button type="button" onClick={onCancel} className="text-gray-400 hover:text-gray-600">
            <Icons.X className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* IPR Info */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <p className="text-sm text-gray-500">IPR Asociada</p>
        <p className="font-medium text-gray-900">{iprNombre || iprId || 'No seleccionada'}</p>
      </div>

      {/* Tipo */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Tipo de Problema</label>
        <div className="grid grid-cols-5 gap-2">
          {TIPOS.map((t) => (
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

      {/* Impacto */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Nivel de Impacto</label>
        <div className="grid grid-cols-4 gap-3">
          {IMPACTOS.map((i) => (
            <button
              key={i}
              type="button"
              onClick={() => setImpacto(i)}
              className={`px-4 py-3 text-sm font-medium rounded-lg border-2 transition-all ${
                impacto === i
                  ? i === 'CRITICO' ? 'bg-red-600 text-white border-red-600' :
                    i === 'ALTO' ? 'bg-orange-500 text-white border-orange-500' :
                    i === 'MEDIO' ? 'bg-yellow-400 text-black border-yellow-400' :
                    'bg-gray-300 text-black border-gray-300'
                  : 'bg-white text-gray-700 border-gray-200 hover:border-gray-300'
              }`}
            >
              {i}
            </button>
          ))}
        </div>
      </div>

      {/* Descripción */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Descripción del Problema *</label>
        <textarea
          value={descripcion}
          onChange={(e) => setDescripcion(e.target.value)}
          rows={4}
          required
          minLength={10}
          placeholder="Describe el problema de manera clara y detallada..."
          className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gore-brand focus:border-transparent resize-none"
        />
      </div>

      {/* Solución Propuesta */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Solución Propuesta (opcional)</label>
        <textarea
          value={solucionPropuesta}
          onChange={(e) => setSolucionPropuesta(e.target.value)}
          rows={3}
          placeholder="Si tienes una propuesta de solución, descríbela aquí..."
          className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gore-brand focus:border-transparent resize-none"
        />
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
          disabled={createProblema.isPending || !iprId || descripcion.length < 10}
          className="px-6 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {createProblema.isPending ? 'Guardando...' : 'Registrar Problema'}
        </button>
      </div>

      {createProblema.isError && (
        <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm">
          Error: {createProblema.error.message}
        </div>
      )}
    </form>
  );
}
