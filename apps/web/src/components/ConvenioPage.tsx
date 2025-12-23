import { ConvenioForm } from './ConvenioForm';
import { ConvenioList } from './ConvenioList';

export function ConvenioPage() {
  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <header className="text-center">
          <h1 className="text-3xl font-bold text-gore-brand">D-FIN: Gestión de Convenios</h1>
          <p className="text-gray-500">Convenios de Programación — GORE Ñuble</p>
        </header>
        
        <ConvenioForm />
        <ConvenioList />
      </div>
    </div>
  );
}
