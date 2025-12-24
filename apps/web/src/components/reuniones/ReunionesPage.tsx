import { useState } from 'react';
import { trpc } from '../../trpc';
import { Icons } from '@gore-os/ui/src/atoms/GoreIcon';

const estadoColor = (estado: string) => {
  switch (estado) {
    case 'EN_CURSO': return 'bg-green-500 text-white';
    case 'PROGRAMADA': return 'bg-blue-400 text-white';
    case 'FINALIZADA': return 'bg-gray-400 text-white';
    default: return 'bg-gray-300 text-black';
  }
};

export function ReunionesPage() {
  const [showForm, setShowForm] = useState(false);
  
  const { data: sesiones, isLoading } = trpc.reunion.list.useQuery();
  const { data: stats } = trpc.reunion.getStats.useQuery();
  const utils = trpc.useUtils();

  const createSesion = trpc.reunion.create.useMutation({
    onSuccess: () => {
      utils.reunion.list.invalidate();
      utils.reunion.getStats.invalidate();
      setShowForm(false);
    },
  });

  const startSesion = trpc.reunion.start.useMutation({
    onSuccess: () => utils.reunion.list.invalidate(),
  });

  const endSesion = trpc.reunion.end.useMutation({
    onSuccess: () => utils.reunion.list.invalidate(),
  });

  const handleCreateSesion = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    createSesion.mutate({
      tipo: formData.get('tipo') as 'ORDINARIA' | 'EXTRAORDINARIA' | 'CRISIS',
      fecha: new Date(formData.get('fecha') as string).toISOString(),
      lugar: formData.get('lugar') as string,
      modalidad: formData.get('modalidad') as 'PRESENCIAL' | 'REMOTA' | 'HIBRIDA',
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-pulse text-lg text-gray-500">Cargando reuniones...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gore-brand mb-2">Sesiones de Crisis</h1>
          <p className="text-gray-600">Gestión de reuniones y puntos de tabla</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-gore-brand text-white rounded-lg hover:bg-gore-brand/90"
        >
          <Icons.Plus className="h-5 w-5" />
          Nueva Sesión
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <p className="text-sm text-gray-500">Total Sesiones</p>
          <p className="text-3xl font-bold">{stats?.total || 0}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <p className="text-sm text-gray-500">En Curso</p>
          <p className="text-3xl font-bold text-green-600">{stats?.enCurso || 0}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <p className="text-sm text-gray-500">Programadas</p>
          <p className="text-3xl font-bold text-blue-600">{stats?.programadas || 0}</p>
        </div>
      </div>

      {/* New Session Form */}
      {showForm && (
        <div className="bg-white rounded-xl shadow-sm border p-6 mb-8">
          <h2 className="text-lg font-semibold mb-4">Crear Nueva Sesión</h2>
          <form onSubmit={handleCreateSesion} className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <select name="tipo" required className="px-3 py-2 border rounded-lg">
              <option value="CRISIS">Crisis</option>
              <option value="ORDINARIA">Ordinaria</option>
              <option value="EXTRAORDINARIA">Extraordinaria</option>
            </select>
            <input type="datetime-local" name="fecha" required className="px-3 py-2 border rounded-lg" />
            <input type="text" name="lugar" placeholder="Lugar" defaultValue="Sala GORE" className="px-3 py-2 border rounded-lg" />
            <select name="modalidad" className="px-3 py-2 border rounded-lg">
              <option value="PRESENCIAL">Presencial</option>
              <option value="REMOTA">Remota</option>
              <option value="HIBRIDA">Híbrida</option>
            </select>
            <button type="submit" disabled={createSesion.isPending} className="md:col-span-4 bg-gore-brand text-white py-2 rounded-lg hover:bg-gore-brand/90 disabled:opacity-50">
              {createSesion.isPending ? 'Creando...' : 'Crear Sesión'}
            </button>
          </form>
        </div>
      )}

      {/* Sessions List */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">N°</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fecha</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Lugar</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sesiones && sesiones.length > 0 ? (
              sesiones.map((s) => (
                <tr key={s.id_sesion} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium">{s.numero}</td>
                  <td className="px-6 py-4 text-sm">{s.tipo_sesion}</td>
                  <td className="px-6 py-4 text-sm">{new Date(s.fecha).toLocaleString('es-CL')}</td>
                  <td className="px-6 py-4 text-sm">{s.lugar}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs rounded-full ${estadoColor(s.estado)}`}>{s.estado}</span>
                  </td>
                  <td className="px-6 py-4 space-x-2">
                    {s.estado === 'PROGRAMADA' && (
                      <button onClick={() => startSesion.mutate({ id: s.id_sesion })} className="text-green-600 hover:underline text-sm">Iniciar</button>
                    )}
                    {s.estado === 'EN_CURSO' && (
                      <button onClick={() => endSesion.mutate({ id: s.id_sesion })} className="text-red-600 hover:underline text-sm">Finalizar</button>
                    )}
                    <a href={`#reunion/${s.id_sesion}`} className="text-gore-brand hover:underline text-sm">Ver</a>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={6} className="px-6 py-8 text-center text-gray-500">No hay sesiones programadas</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
