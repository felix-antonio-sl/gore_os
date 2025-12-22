#!/bin/bash

# Configuration
KC_ADM="/opt/keycloak/bin/kcadm.sh"
REALM="gore_os"
CLIENT_ID="gore-web"
USER_NAME="admin-gore"
USER_PASS="1234"

echo "⏳ Waiting for Keycloak to be ready..."
until curl -s http://localhost:8080/health > /dev/null; do
    sleep 2
    echo "..."
done

echo "🔐 Authenticating as admin..."
docker exec -i gore_auth $KC_ADM config credentials --server http://localhost:8080 --realm master --user admin --password admin

echo "🌍 Creating Realm '$REALM'..."
# Check if realm exists, if not create it
docker exec -i gore_auth $KC_ADM get realms/$REALM > /dev/null 2>&1
if [ $? -ne 0 ]; then
    docker exec -i gore_auth $KC_ADM create realms -s realm=$REALM -s enabled=true
    echo "✅ Realm created."
else
    echo "ℹ️ Realm already exists."
fi

echo "💻 Creating Client '$CLIENT_ID'..."
CID=$(docker exec -i gore_auth $KC_ADM get clients -r $REALM -q clientId=$CLIENT_ID --fields id --format csv --noquotes)
if [ -z "$CID" ]; then
    docker exec -i gore_auth $KC_ADM create clients -r $REALM \
        -s clientId=$CLIENT_ID \
        -s enabled=true \
        -s protocol=openid-connect \
        -s publicClient=true \
        -s 'redirectUris=["http://localhost/*"]' \
        -s 'webOrigins=["+"]'
    echo "✅ Client created."
else
    echo "ℹ️ Client already exists."
fi

echo "👤 Creating User '$USER_NAME'..."
UID=$(docker exec -i gore_auth $KC_ADM get users -r $REALM -q username=$USER_NAME --fields id --format csv --noquotes)
if [ -z "$UID" ]; then
    docker exec -i gore_auth $KC_ADM create users -r $REALM \
        -s username=$USER_NAME \
        -s enabled=true \
        -s email=admin@gore.cl \
        -s firstName=Admin \
        -s lastName=GORE
    
    # Set password
    docker exec -i gore_auth $KC_ADM set-password -r $REALM --username $USER_NAME --new-password $USER_PASS
    
    # Get ID again to assign roles
    UID=$(docker exec -i gore_auth $KC_ADM get users -r $REALM -q username=$USER_NAME --fields id --format csv --noquotes)
    echo "✅ User created."
else
    echo "ℹ️ User already exists."
fi

echo "👑 Assigning Admin Role..."
# Get realm-admin role from realm-management client logic is complex specifically, 
# for simplicity we will just assume standard realm setup.
# Actually, let's just create a simpler App Role 'admin'
docker exec -i gore_auth $KC_ADM get roles -r $REALM admin > /dev/null 2>&1
if [ $? -ne 0 ]; then
    docker exec -i gore_auth $KC_ADM create roles -r $REALM -s name=admin
fi
docker exec -i gore_auth $KC_ADM add-roles -r $REALM --uusername $USER_NAME --rolename admin

echo "🚀 Keycloak Configuration Complete!"
echo "   Realm: $REALM"
echo "   Client: $CLIENT_ID"
echo "   User: $USER_NAME / $USER_PASS"
