import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { trpc } from '../../trpc';
import { IPRPage } from './IPRPage'; // Just for context, component is separate

// Schema aligned with API input
const CreateIPRSchema = z.object({
  nombre: z.string().min(5, "El nombre debe tener al menos 5 caracteres"),
  fondoId: z.string().min(1, "Debe seleccionar un fondo"),
  montoTotal: z.number({ invalid_type_error: "Debe ser un número" }).int().nonnegative("El monto no puede ser negativo"),
  comunaId: z.string().uuid("Debe seleccionar una comuna válida"),
  fechaPostulacion: z.string().datetime().optional() // We'll set default
});

type CreateIPRFormValues = z.infer<typeof CreateIPRSchema>;

interface IPRFormProps {
  onSuccess: () => void;
  onCancel: () => void;
}

export const IPRForm = ({ onSuccess, onCancel }: IPRFormProps) => {
  const utils = trpc.useContext();
  const createMutation = trpc.ipr.create.useMutation({
    onSuccess: () => {
      utils.ipr.list.invalidate(); // Refresh list
      onSuccess();
    }
  });

  const { register, handleSubmit, formState: { errors } } = useForm<CreateIPRFormValues>({
    resolver: zodResolver(CreateIPRSchema),
    defaultValues: {
      fondoId: "FNDR", // Default
      montoTotal: 0,
      comunaId: "e2c3a5b0-1f22-4d56-8c43-2287f345d3e2", // Placeholder Chillan (should fetch from API)
    }
  });

  const onSubmit = (data: CreateIPRFormValues) => {
    createMutation.mutate({
      ...data,
      fechaPostulacion: new Date().toISOString(), // Auto set date
      // Optional fields handled by API defaults
    });
  };

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-medium text-gore-brand">Nueva Iniciativa de Inversión</h2>
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        
        {/* Nombre */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Nombre Iniciativa</label>
          <input 
            {...register('nombre')}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gore-brand focus:ring-gore-brand sm:text-sm p-2 border"
            placeholder="Ej: Construcción Sede Social..."
          />
          {errors.nombre && <p className="text-sm text-red-600">{errors.nombre.message}</p>}
        </div>

        {/* Fondo */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Fondo de Financiamiento</label>
          <select 
            {...register('fondoId')}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gore-brand focus:ring-gore-brand sm:text-sm p-2 border"
          >
             <option value="FNDR">FNDR - Fondo Nacional Desarrollo Regional</option>
             <option value="FRIL">FRIL - Fondo Regional Iniciativa Local</option>
          </select>
          {errors.fondoId && <p className="text-sm text-red-600">{errors.fondoId.message}</p>}
        </div>

        {/* Monto */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Monto Estimado (CLP)</label>
          <input 
            type="number"
            {...register('montoTotal', { valueAsNumber: true })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-gore-brand focus:ring-gore-brand sm:text-sm p-2 border"
          />
          {errors.montoTotal && <p className="text-sm text-red-600">{errors.montoTotal.message}</p>}
        </div>

        {/* Buttons */}
        <div className="flex justify-end gap-2 pt-4">
          <button
            type="button"
            onClick={onCancel}
            className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={createMutation.isLoading}
            className="inline-flex justify-center rounded-md border border-transparent bg-gore-brand px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-gore-brand/90 focus:outline-none disabled:opacity-50"
          >
            {createMutation.isLoading ? 'Creando...' : 'Crear IPR'}
          </button>
        </div>

        {createMutation.error && (
            <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
                Error: {createMutation.error.message}
            </div>
        )}

      </form>
    </div>
  );
};
