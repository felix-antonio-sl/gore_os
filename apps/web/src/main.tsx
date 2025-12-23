import React from 'react';
import ReactDOM from 'react-dom/client';
import { ReactKeycloakProvider } from '@react-keycloak/web';
import keycloak from './keycloak';
import App from './App';
import './index.css';

import { UiShowcase } from './UiShowcase';

const isUiShowcase = window.location.hash === "#ui";

const rootElement = document.getElementById('root')!;
const root = ReactDOM.createRoot(rootElement);

if (isUiShowcase) {
  root.render(
    <React.StrictMode>
      <UiShowcase />
    </React.StrictMode>
  );
} else {
  root.render(
    <React.StrictMode>
      <ReactKeycloakProvider 
        authClient={keycloak}
        initOptions={{ onLoad: 'login-required', checkLoginIframe: false }}
      >
        <App />
      </ReactKeycloakProvider>
    </React.StrictMode>
  );
}
