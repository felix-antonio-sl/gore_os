# Despliegue desde una revisión fija

La API y la web deben consumir imágenes preparadas desde el mismo commit. La
receta [compose.production.yml](../compose.production.yml) conserva PostgreSQL
como servicio externo: no inicializa, migra ni sustituye su base o volumen.

`docker-compose.yml` sigue siendo la receta de desarrollo. Sus montajes de
código y su compilación al arrancar no forman parte del despliegue de producción.

## Preparar la entrega

Exporta un SHA completo en un directorio de entrega nuevo, sin `.env`, derivados
ni cambios del checkout. Usa el lockfile y las versiones existentes; un cambio
de dependencias requiere su propia verificación.

```bash
revision="$(git rev-parse HEAD)"
release_dir="${XDG_DATA_HOME:-$HOME/.local/share}/gore-os/releases/$revision"
mkdir -p "$release_dir"
git archive "$revision" | tar -x -C "$release_dir"
```

Prepara la web dentro de esa entrega. `NEXT_PUBLIC_API_URL` queda integrado en el
JavaScript durante la compilación: debe ser el destino real que ya consumen los
navegadores, sin alterar el perímetro ni el proxy existente.

```bash
cd "$release_dir/web"
npm ci
NEXT_PUBLIC_API_URL="https://goreos.sanixai.com" npm run build
docker build -f Dockerfile.production \
  --build-arg GORE_REVISION="$revision" \
  -t "gore-os-web:$revision" .
cd "$release_dir/api"
docker build -f Dockerfile.production \
  --build-arg GORE_REVISION="$revision" \
  -t "gore-os-api:$revision" .
```

El servidor `standalone` de Next.js incluye las dependencias trazadas y
`server.js`; la imagen añade `public` y `.next/static`, como exige la
[documentación de Next.js](https://nextjs.org/docs/app/api-reference/config/next-config-js/output).
Al reutilizar imágenes y dependencias ya verificadas, los argumentos
`NODE_IMAGE` y `PYTHON_IMAGE` permiten fijar sus IDs locales o digests. Elimina
del contexto de compilación cualquier salida anterior. Verifica siempre el
build resultante y el recorrido con una base aislada antes de consumirlo.

## Configuración y arranque

Mantén fuera del repositorio un directorio privado con `api.env` y
`production.env` (directorio 700, archivos 600). La API no monta código ni
estado de desarrollo; la carpeta externa histórica de captura de bugs permanece
conservada por el operador. `api.env` conserva la conexión
PostgreSQL, JWT, CORS y el modo de API existentes; no cambia la autenticación al
pasar a imágenes preparadas. `production.env` fija estos valores:

| Variable | Contrato |
|----------|----------|
| `GORE_REVISION` | SHA completo de la entrega y de ambas imágenes |
| `GORE_API_IMAGE`, `GORE_WEB_IMAGE` | IDs inmutables locales o digests de las imágenes verificadas |
| `GORE_CONFIG_DIR` | Directorio privado que contiene `api.env` |
| `GORE_DOMAIN` | Host del proxy existente |
| `GOREOS_BASICAUTH` | Valor BasicAuth existente; entre comillas simples en el archivo dotenv |

```bash
docker compose -p gore-os-production \
  --env-file "$private_config/production.env" \
  -f "$release_dir/compose.production.yml" config --quiet
docker compose -p gore-os-production \
  --env-file "$private_config/production.env" \
  -f "$release_dir/compose.production.yml" up -d --no-build --pull never
```

La API ejecuta Uvicorn sin `--reload`; la web ejecuta `node server.js`. Sus
imágenes incluyen el código. La API no tiene montajes de código ni estado mutable
de desarrollo; la web no monta código, dependencias ni builds.
Los puertos siguen en loopback y ambas redes externas, las rutas TLS y el
middleware BasicAuth del frontend se conservan. La API conserva su control JWT.

`/api/health` acredita el proceso HTTP. La disponibilidad funcional exige además
una base con el esquema y las identidades autorizadas. Una base vacía no se
aprovisiona por el mero hecho de desplegar una revisión de código.

## Inicializar una base vacía autorizada

La inicialización requiere una decisión expresa sobre esa base y un respaldo
restaurado en laboratorio. Desde la entrega fija, la receta
`scripts/bootstrap_empty_db.py` aplica el DDL y los catálogos de referencia
canónicos, además de los 25 territorios (código, nombre, tipo y jerarquía).
Excluye estadísticas, indicadores y organizaciones del seed territorial,
usuarios nominales, miembros CORE, expedientes, demos, ETL y registros que
simulen migraciones realizadas. No atribuye cargos ni ratificación institucional.

```bash
python3 "$release_dir/scripts/bootstrap_empty_db.py" \
  --container goreos_db --database goreos_model --user goreos --prepare-only
python3 "$release_dir/scripts/bootstrap_empty_db.py" \
  --container goreos_db --database goreos_model --user goreos
```

El guard dentro de la transacción rechaza cualquier base con tablas o schemas
de aplicación existentes. El DDL y los catálogos se aplican como una sola
transacción; la receta no crea, elimina ni sustituye bases o volúmenes. Emite
sólo los hashes de fuente, el hash del SQL preparado y las exclusiones.

La cuenta inicial se prepara por separado, sólo cuando está autorizada. Utiliza
una identidad técnica explícita y el rol de administración del sistema, con
RUT, cargo, estamento, organización y división vacíos. La contraseña se genera
privadamente y se conserva fuera del repositorio con permisos 600; la base
recibe su hash con el mecanismo de autenticación existente. Esa cuenta habilita
el acceso técnico y no representa a un funcionario. Verifica login, bandeja
vacía y rechazos de acceso, y respalda y restaura después el nuevo estado.

## Recuperación

Antes de sustituir contenedores, conserva los IDs de imágenes, configuración y
montajes previos, una copia congelada de la fuente anterior y los builds
necesarios. El rollback debe consumir esa copia, aunque el checkout haya cambiado.
Conserva también los volcados privados de PostgreSQL y de roles globales.

Prueba los volcados con la misma versión de PostgreSQL en un contenedor sin red
ni puertos, restaurando sobre bases vacías creadas con `template0`. Excluye del
volcado global sólo los `CREATE ROLE` que ya existen en ese clon. Compara
recuentos y huellas sin emitir filas. No ejecutes trabajos cron en la copia.

Para una copia custom de la base GORE inicializada, prepara los roles y el
target vacío antes de ejecutar la receta versionada:

```bash
python3 "$release_dir/scripts/restore_empty_db.py" \
  --container "$isolated_pg" --database goreos_model --user goreos \
  --archive "$private_backup/goreos_model.dump"
```

Los CHECK de `core` consultan `ref.category`. La receta adelanta los TABLE DATA
de `ref` y mantiene todas las entradas del dump, funciones, CHECK y triggers.
Usa un archivo custom seekable dentro del contenedor privado y una sola
transacción; no desactiva controles ni elimina objetos. Rechaza un target con
tablas o schemas de aplicación. Verifica después sus recuentos y huellas contra
la copia; cada nuevo estado de datos exige comprobar su recuperación.

Prueba la receta de rollback en puertos de laboratorio y documenta qué recupera.
Si sólo cambia el código, el rollback conserva la base original. Restaurar datos
o reconectar un volumen anterior exige conocer su procedencia, compatibilidad y
la decisión autorizada para ese estado; nunca se sustituye por un seed.
