# pruebas/ · prueba de carga

```bash
pip install locust==2.32.4
API_KEY=<tu clave> locust -f pruebas/locustfile.py \
  --host https://54-164-114-132.sslip.io --headless -u 20 -r 5 -t 3m --csv carga
```

Antes de medir:

1. Sube `LIMITE_POR_MINUTO` en el `.env` de la EC2 (por ejemplo a 2000) y
   `docker compose up -d dominio`. Si no, la corrida mide el rate limiting y no
   el sistema. Bajalo despues.
2. Calienta el endpoint: `curl` tres o cuatro veces `/api/predict` antes de
   lanzar Locust. Un endpoint serverless dormido tarda unos 6 s en la primera
   invocacion y eso contamina el p95 de toda la corrida.
3. Corre Locust desde tu notebook, no desde la EC2.

Los resultados van al apartado 5 del informe: solicitudes, errores, req/s, p50,
p95 y p99.
