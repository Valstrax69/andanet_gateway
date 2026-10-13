# gateway — API gateway (Nginx)

Única puerta de entrada del sistema. Publica el puerto **8080** y enruta:

- `/` → `front`
- `/api/chat` → `dominio`
- `/api/predict` → `ia` (2 réplicas; el gateway reparte entre ellas)

El balanceo usa el DNS interno de Docker: al poner el nombre de servicio `ia`
dentro de una variable, Nginx lo re-resuelve en cada petición y el DNS entrega
las réplicas por turnos. `resolver 127.0.0.11 valid=1s`.

> Este repo contiene el **`compose.yaml` de la defensa** (anexo C) y el
> `.env.example`. Ver el README raíz del workspace para levantar el sistema.

## Construir
```bash
docker build -t gateway .
```
