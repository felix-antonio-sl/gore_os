import { Button } from '@gore-os/ui';

function App() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4 text-blue-600">GORE_OS</h1>
        <p className="mb-4 text-gray-600">Sistema de Gestión Regional</p>
        <div className="p-4 border rounded bg-white shadow">
            <p className="mb-2">UI Package Integration:</p>
            <Button />
        </div>
      </div>
    </div>
  );
}

export default App;
