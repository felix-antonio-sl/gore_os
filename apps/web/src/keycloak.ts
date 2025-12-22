import Keycloak from 'keycloak-js';

const keycloak = new Keycloak({
  url: 'http://localhost:8080',
  realm: 'gore_os',
  clientId: 'gore-web',
});

export default keycloak;
