# KIU Challenge — Levantar con Docker

## Requisitos

- Docker + Docker Compose

## Variables de entorno

Crear un archivo **`.env`** en la raíz del repo con:

```env
FLIGHT_EVENTS_PATH=/app/app/resources/flight_events.json
```

## Build & Run

```bash
docker compose up -d --build
```

## Probar

### Health

```bash
curl http://localhost:8000/health
```

### Búsqueda de vuelos

```bash
curl -G "http://localhost:8000/api/v1/journeys/search"   --data-urlencode "date=2021-12-31"   --data-urlencode "from=MAD"   --data-urlencode "to=BUE"
```

## Docs

```bash
http://localhost:8000/docs#/
```

## Logs / Detener

```bash
docker compose logs -f api   # ver logs
docker compose down          # detener y limpiar
```
