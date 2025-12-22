import React from 'react';
import ReactDOM from 'react-dom/client';
import { ReactKeycloakProvider } from '@react-keycloak/web';
import keycloak from './keycloak';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ReactKeycloakProvider 
      authClient={keycloak}
      initOptions={{ onLoad: 'login-required', checkLoginIframe: false }}
    >
      <App />
    </ReactKeycloakProvider>
  </React.StrictMode>
);
