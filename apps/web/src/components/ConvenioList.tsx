import { trpc } from '../trpc';
import { GoreBadge } from '@gore-os/ui';
import { Formatters } from '@gore-os/ui';

export function ConvenioList() {
  const { data: convenios, isLoading, isError } = trpc.convenio.list.useQuery();

  if (isLoading) return <div className="text-center p-4">Cargando convenios...</div>;
  if (isError) return <GoreBadge variant="destructive">Error cargando convenios</GoreBadge>;

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="bg-gore-brand text-white px-4 py-3 font-semibold">
        Convenios Registrados ({convenios?.length || 0})
      </div>
      <ul className="divide-y divide-gray-200">
        {convenios?.map((c) => (
          <li key={c.id} className="p-4 hover:bg-gray-50 transition-colors">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-medium text-gray-900">{c.nombre}</h3>
                <p className="text-sm text-gray-500">{c.ministerio}</p>
              </div>
              <div className="text-right">
                <p className="text-lg font-bold text-gore-secondary">
                  {Formatters.formatCurrency(Number(c.montoTotal))}
                </p>
                <GoreBadge variant={c.estado === 'VIGENTE' ? 'success' : 'outline'}>
                  {c.estado}
                </GoreBadge>
              </div>
            </div>
          </li>
        ))}
        {convenios?.length === 0 && (
          <li className="p-4 text-center text-gray-400">No hay convenios registrados</li>
        )}
      </ul>
    </div>
  );
}
