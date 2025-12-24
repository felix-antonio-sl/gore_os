import { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { httpBatchLink } from '@trpc/client';
import { useKeycloak } from '@react-keycloak/web';
import { trpc } from './trpc';
import { Button } from '@gore-os/ui';
import { UiShowcase } from './UiShowcase';
import { ConvenioPage } from './components/ConvenioPage';
import { EntityExplorer } from './components/EntityExplorer';

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

import { IPRPage } from './components/ipr/IPRPage';
import { CrisisPage } from './components/crisis/CrisisPage';
import { ReunionesPage } from './components/reuniones/ReunionesPage';
import keycloak from './keycloak';

// 1. AppShell: Handles minimal routing based on Hash (No Keycloak Hook here!)
function AppShell() {
  const [hash, setHash] = useState(window.location.hash);

  useEffect(() => {
    const handleHashChange = () => setHash(window.location.hash);
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const isUiShowcase = hash === "#ui";
  const isIpr = hash === "#ipr";
  const isCrisis = hash === "#crisis";
  const isReuniones = hash === "#reuniones";
  const isHome = hash === "#home" || hash === "" || hash === "#";

  // Bypass Config - Stable Instances
  const [queryClient] = useState(() => new QueryClient());
  const [trpcClient] = useState(() => 
    trpc.createClient({
      links: [ httpBatchLink({ url: '/trpc' }) ],
    })
  );

  // Home/Explorer route - No auth required
  if (isHome) {
    return <EntityExplorer />;
  }

  if (isUiShowcase) {
    return (
      <div className="min-h-screen bg-gray-100">
        <UiShowcase />
      </div>
    );
  }

  if (isIpr) {
    return (
      <trpc.Provider client={trpcClient} queryClient={queryClient}>
        <QueryClientProvider client={queryClient}>
          <div className="min-h-screen bg-gray-50 flex flex-col">
            <header className="bg-white border-b px-8 py-4 flex justify-between items-center">
               <div className="font-bold text-gore-brand text-xl">GORE_OS <span className="text-gray-400 font-normal">| M1 Portafolio</span></div>
               <div className="space-x-4 flex items-center">
                  <a href="#crisis" className="text-sm text-gore-brand hover:underline">Centro de Crisis</a>
                  <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">Modo Desarrollo (Bypass Auth)</span>
                  <a href="/" className="text-sm text-gray-500 hover:underline">Ir a Home</a>
               </div>
            </header>
            <main className="flex-1">
              <IPRPage />
            </main>
          </div>
        </QueryClientProvider>
      </trpc.Provider>
    );
  }

  if (isCrisis) {
    return (
      <trpc.Provider client={trpcClient} queryClient={queryClient}>
        <QueryClientProvider client={queryClient}>
          <div className="min-h-screen bg-gray-50 flex flex-col">
            <header className="bg-white border-b px-8 py-4 flex justify-between items-center">
               <div className="font-bold text-gore-brand text-xl">GORE_OS <span className="text-gray-400 font-normal">| Centro de Crisis</span></div>
               <div className="space-x-4 flex items-center">
                  <a href="#ipr" className="text-sm text-gore-brand hover:underline">Portafolio IPR</a>
                  <a href="#reuniones" className="text-sm text-gore-brand hover:underline">Reuniones</a>
                  <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">Gestión de Crisis</span>
                  <a href="/" className="text-sm text-gray-500 hover:underline">Ir a Home</a>
               </div>
            </header>
            <main className="flex-1">
              <CrisisPage />
            </main>
          </div>
        </QueryClientProvider>
      </trpc.Provider>
    );
  }

  if (isReuniones) {
    return (
      <trpc.Provider client={trpcClient} queryClient={queryClient}>
        <QueryClientProvider client={queryClient}>
          <div className="min-h-screen bg-gray-50 flex flex-col">
            <header className="bg-white border-b px-8 py-4 flex justify-between items-center">
               <div className="font-bold text-gore-brand text-xl">GORE_OS <span className="text-gray-400 font-normal">| Sesiones de Crisis</span></div>
               <div className="space-x-4 flex items-center">
                  <a href="#crisis" className="text-sm text-gore-brand hover:underline">Centro de Crisis</a>
                  <a href="#ipr" className="text-sm text-gore-brand hover:underline">Portafolio IPR</a>
                  <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">Reuniones</span>
                  <a href="/" className="text-sm text-gray-500 hover:underline">Ir a Home</a>
               </div>
            </header>
            <main className="flex-1">
              <ReunionesPage />
            </main>
          </div>
        </QueryClientProvider>
      </trpc.Provider>
    );
  }

  // 2. Default: Render Keycloak Provider for Protected App
  return (
    <ReactKeycloakProvider 
      authClient={keycloak}
      initOptions={{ 
        onLoad: 'login-required', 
        checkLoginIframe: false,
        redirectUri: 'http://localhost:5173'
      }}
    >
      <AuthenticatedApp hash={hash} setHash={setHash} />
    </ReactKeycloakProvider>
  );
}

// 3. AuthenticatedApp: Can safely use useKeycloak hook
function AuthenticatedApp({ hash, setHash }: { hash: string, setHash: (h: string) => void }) {
  const { keycloak, initialized } = useKeycloak();
  
  // Auth-aware Clients - Stable Instances
  const [queryClient] = useState(() => new QueryClient());
  const [trpcClient] = useState(() => 
    trpc.createClient({
      links: [
        httpBatchLink({
          url: '/trpc',
          headers: () => ({
            Authorization: keycloak.token ? `Bearer ${keycloak.token}` : '',
          }),
        }),
      ],
    })
  );

  const isConvenios = hash === "#convenios";

  if (!initialized) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center space-y-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gore-brand"></div>
        <div className="text-gore-text font-medium">Cargando autenticación...</div>
        <div className="text-xs text-gray-400">Verificando conexión con Keycloak (localhost:8080)</div>
        <div className="flex flex-col gap-2 mt-8">
          <button 
            onClick={() => {
              window.location.hash = "#ipr";
              window.location.reload();
            }} 
            className="text-sm text-gore-brand font-bold underline"
          >
            Ir a Portafolio IPR (M1) - Sin Autenticación
          </button>
        </div>
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
                <div className="text-center mt-8 space-x-4 flex justify-center items-center">
                    <a href="#ipr" className="text-gore-brand font-bold underline hover:text-gore-brand/80" onClick={() => setHash('#ipr')}>M1: Portafolio IPR</a>
                    <span className="text-gray-300">|</span>
                    <a href="#convenios" className="text-gray-600 underline hover:text-gray-800" onClick={() => setHash('#convenios')}>D-FIN: Convenios</a>
                    <span className="text-gray-300">|</span>
                    <a href="#ui" className="text-blue-600 underline hover:text-blue-800" onClick={() => setHash('#ui')}>UI Showcase</a>
                </div>
            </div>
        </div>
      </QueryClientProvider>
    </trpc.Provider>
  );
}

function App() {
  return <AppShell />;
}

export default App;
