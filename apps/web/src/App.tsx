import { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { httpBatchLink } from '@trpc/client';
import { useKeycloak } from '@react-keycloak/web';
import { trpc } from './trpc';
import { Button } from '@gore-os/ui';
import { UiShowcase } from './UiShowcase';
import { ConvenioPage } from './components/ConvenioPage';

function LogViewer() {
  const [message, setMessage] = useState('');
  const { keycloak } = useKeycloak();
  const utils = trpc.useUtils();
  const logs = trpc.getLogs.useQuery();
  const addLog = trpc.addLog.useMutation({
    onSuccess: () => {
      setMessage('');
      utils.getLogs.invalidate();
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      addLog.mutate({ message });
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-xl shadow-lg space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">GORE_OS E2E Test</h2>
        <button 
          onClick={() => keycloak.logout()}
          className="text-sm text-red-600 hover:underline"
        >
          Cerrar Sesión
        </button>
      </div>
      
      <p className="text-sm text-gray-500">
        👤 Usuario: <strong>{keycloak.tokenParsed?.preferred_username || 'N/A'}</strong>
      </p>
      
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Escribe un mensaje..."
          className="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={addLog.isPending}
        />
        <Button /> 
        <button 
            type="submit" 
            disabled={addLog.isPending}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {addLog.isPending ? 'Enviando...' : 'Enviar'}
        </button>
      </form>

      <div className="border-t pt-4">
        <h3 className="text-lg font-semibold mb-2">Logs en DB:</h3>
        {logs.isLoading ? (
          <p className="text-gray-500">Cargando...</p>
        ) : (
          <ul className="space-y-2">
            {logs.data?.map((log) => (
              <li key={log.id} className="text-sm bg-gray-50 p-2 rounded border">
                <span className="font-mono text-xs text-gray-400">[{new Date(log.createdAt).toLocaleTimeString()}]</span> {log.message}
              </li>
            ))}
            {logs.data?.length === 0 && <p className="text-gray-400 italic">No hay logs aún.</p>}
          </ul>
        )}
      </div>
    </div>
  );
}

function AppContent() {
  const { keycloak, initialized } = useKeycloak();
  // Estado reactivo para el hash
  const [hash, setHash] = useState(window.location.hash);

  useEffect(() => {
    const handleHashChange = () => setHash(window.location.hash);
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const queryClient = new QueryClient();
  
  const trpcClient = trpc.createClient({
    links: [
      httpBatchLink({
        url: '/trpc',
        headers: () => ({
          Authorization: keycloak.token ? `Bearer ${keycloak.token}` : '',
        }),
      }),
    ],
  });

  const isUiShowcase = hash === "#ui";
  const isConvenios = hash === "#convenios";

  if (!initialized && !isUiShowcase && !isConvenios) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center space-y-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gore-brand"></div>
        <div className="text-gore-text font-medium">Cargando autenticación...</div>
        <div className="text-xs text-gray-400">Verificando conexión con Keycloak (localhost:8080)</div>
        <button 
          onClick={() => {
            window.location.hash = "#ui";
            window.location.reload();
          }} 
          className="mt-8 text-sm text-blue-600 underline"
        >
          Saltar a UI Showcase (Sin Autenticación)
        </button>
      </div>
    );
  }

  if (isUiShowcase) {
    return (
      <div className="min-h-screen bg-gray-100">
        <UiShowcase />
      </div>
    );
  }

  if (isConvenios) {
    return (
      <trpc.Provider client={trpcClient} queryClient={queryClient}>
        <QueryClientProvider client={queryClient}>
          <ConvenioPage />
        </QueryClientProvider>
      </trpc.Provider>
    );
  }

  if (!keycloak.authenticated) {
    return <div className="min-h-screen flex items-center justify-center">Redirigiendo a login...</div>;
  }

  return (
    <trpc.Provider client={trpcClient} queryClient={queryClient}>
      <QueryClientProvider client={queryClient}>
        <div className="min-h-screen bg-gray-100">
            <div className="py-12">
                <LogViewer />
                <div className="text-center mt-8 space-x-4">
                    <a href="#convenios" className="text-gore-brand underline hover:text-gore-brand/80" onClick={() => setHash('#convenios')}>D-FIN: Convenios</a>
                    <a href="#ui" className="text-blue-600 underline hover:text-blue-800" onClick={() => setHash('#ui')}>UI Showcase</a>
                </div>
            </div>
        </div>
      </QueryClientProvider>
    </trpc.Provider>
  );
}

function App() {
  return <AppContent />;
}

export default App;
