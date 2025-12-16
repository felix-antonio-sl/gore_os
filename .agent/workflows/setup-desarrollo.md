---
description: Levantar entorno de desarrollo local con Docker
---

# Workflow: Setup Desarrollo Local

Este workflow configura el entorno de desarrollo local usando Docker Compose.

---

## Pasos

### 1. Verificar requisitos

// turbo
```bash
docker --version && docker compose version && bun --version
```

Versiones requeridas:
- Docker >= 24
- Docker Compose >= 2.20
- Bun >= 1.1

### 2. Clonar repositorio

```bash
git clone git@github.com:gore-nuble/gore-os.git
cd gore-os
```

### 3. Copiar variables de entorno

// turbo
```bash
cp .env.example .env
```

### 4. Levantar servicios base

// turbo
```bash
docker compose up -d postgres redis keycloak
```

### 5. Esperar que servicios estén listos

// turbo
```bash
docker compose logs -f postgres --until=30s | grep -m1 "ready to accept connections"
```

### 6. Instalar dependencias

// turbo
```bash
bun install
```

### 7. Aplicar migraciones

// turbo
```bash
bun db:migrate
```

### 8. Seed de datos (opcional)

// turbo
```bash
bun db:seed
```

### 9. Levantar desarrollo

// turbo
```bash
bun dev
```

---

## Servicios Disponibles

| Servicio   | URL                   | Credenciales      |
| ---------- | --------------------- | ----------------- |
| API        | http://localhost:3000 | -                 |
| Frontend   | http://localhost:5173 | -                 |
| Keycloak   | http://localhost:8080 | admin/admin       |
| PostgreSQL | localhost:5432        | postgres/postgres |
| Redis      | localhost:6379        | -                 |

---

## Troubleshooting

### Puerto en uso

```bash
lsof -i :3000
kill -9 <PID>
```

### Limpiar todo y reiniciar

```bash
docker compose down -v
rm -rf node_modules
bun install
docker compose up -d
```
