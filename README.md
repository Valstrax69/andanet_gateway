# gateway — API gateway (Nginx)

Única puerta de entrada del sistema ANDA (asistente de atención de Andesnet).
Publica el puerto **8080** y enruta:

- `/` → `front`
- `/api/chat` → `dominio`
- `/api/predict` → `ia` (2 réplicas; el gateway reparte entre ellas)

El balanceo usa el DNS interno de Docker: al poner el nombre de servicio `ia`
dentro de una variable, Nginx lo re-resuelve en cada petición y el DNS entrega
las réplicas por turnos. `resolver 127.0.0.11 valid=1s`.

Este repositorio contiene el **`compose.yaml` de la defensa** y el `.env.example`.

---

## Levantar el sistema

No hace falta clonar los otros repositorios ni construir imágenes: el
`compose.yaml` solo descarga las imágenes `:ep2` ya publicadas en GHCR, que son
públicas. Se necesita Docker Desktop corriendo y el puerto 8080 libre.

```bash
git clone https://github.com/Valstrax69/andanet_gateway
cd andanet_gateway
copy .env.example .env          # en Linux o macOS: cp .env.example .env
docker compose -p equipo06 pull
docker compose -p equipo06 up -d
```

Luego abrir **http://localhost:8080**. No hay inicio de sesión: el chat está
disponible de inmediato.

La descarga son unos 900 MB y demora entre 1 y 5 minutos según la conexión. El
arranque posterior toma unos 30 segundos.

## Comprobar que quedó arriba

```bash
docker compose -p equipo06 ps
```

Se esperan seis contenedores: `db`, `dominio`, `front`, `gateway` y dos de `ia`,
todos en `Up (healthy)`. El séptimo, `carga`, aparece como **`Exited (0)`** y eso
es correcto: es un trabajo que corre una sola vez, llena la base y termina.

## Apagar

```bash
docker compose -p equipo06 down -v
```

El `-v` borra también el volumen de la base de datos.

## Qué se levanta

| Servicio | Imagen | Para qué sirve |
|---|---|---|
| `front` | `ghcr.io/valstrax69/front:ep2` | La página del chat |
| `gateway` | `ghcr.io/valstrax69/gateway:ep2` | Puerta de entrada y balanceo (único puerto publicado) |
| `dominio` | `ghcr.io/valstrax69/dominio:ep2` | Lógica del asistente: responde o deriva, y registra la predicción |
| `ia` ×2 | `ghcr.io/valstrax69/ia:ep2` | Clasificador de intención y enmascarado de datos personales |
| `db` | `postgres:16-alpine` | Base de datos |
| `carga` | `ghcr.io/valstrax69/carga:ep2` | Carga las tablas tratadas al arrancar y termina |

## Variables de entorno

Se definen en el `.env` (copiado desde `.env.example`). Todas traen un valor de
demostración que funciona tal cual.

| Variable | Para qué sirve | Valor por defecto |
|---|---|---|
| `OWNER` | Cuenta de GitHub donde están las imágenes, en minúsculas | `valstrax69` |
| `REGISTRY` | Registro de contenedores | `ghcr.io` |
| `TAG` | Etiqueta de las imágenes a descargar | `ep2` |
| `POSTGRES_USER` | Usuario de la base (credencial de demostración) | `anda` |
| `POSTGRES_PASSWORD` | Clave de la base (credencial de demostración) | `anda` |
| `POSTGRES_DB` | Nombre de la base | `anda` |
| `UMBRAL_CONFIANZA` | Confianza mínima para responder; bajo ese valor el asistente deriva a un ejecutivo | `0.55` |

Cambiar `UMBRAL_CONFIANZA` y correr `docker compose -p equipo06 up -d dominio`
aplica el nuevo umbral sin reconstruir ninguna imagen. Subirlo acierta más y
responde menos; bajarlo responde más y se equivoca más. La medición de ese
compromiso está en el capítulo 8.4 del documento de arquitectura.

## Construir la imagen del gateway (solo para desarrollo)

```bash
docker build -t gateway .
```
