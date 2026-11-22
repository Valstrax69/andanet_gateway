"""
Prueba de carga de POST /api/predict (EP3 4.3).

    pip install locust==2.32.4
    API_KEY=<tu clave> locust -f pruebas/locustfile.py \
        --host https://54-164-114-132.sslip.io \
        --headless -u 20 -r 5 -t 3m --csv carga

Deja carga_stats.csv con p50, p95, p99, solicitudes por segundo y errores. Esos
numeros van al apartado 5 del informe.

Tres cosas que cambian el resultado y hay que cuidar:

1. NO se mide el camino del LLM. El LLM se llama desde el worker, por la cola,
   despues de responder: medirlo aqui mediria el limite de NVIDIA, no el
   sistema. El camino del LLM se mide aparte, con pocas solicitudes.

2. El limite por minuto se va a disparar. Con 20 usuarios se pasan las 60
   solicitudes por minuto en segundos y empiezan los 429. Para medir el sistema
   hay que subir LIMITE_POR_MINUTO en el .env del servidor mientras dura la
   prueba, y bajarlo despues. Los 429 no son un error: son el limite
   funcionando, y se informan aparte.

3. Correr Locust desde el notebook, NO desde la EC2. En la EC2 competiria por
   los 2 vCPU con todo lo que se esta midiendo, y el numero saldria peor de lo
   que es.

Y calentar el endpoint antes de medir: si el primer escalon golpea un endpoint
serverless dormido, el arranque en frio (unos 6 s) contamina el p95 de toda la
corrida. Conviene informar una corrida en frio y otra en caliente, por separado.
"""
import itertools
import os

from locust import HttpUser, between, task

# Mensajes de las seis intenciones, para que la carga se parezca al trafico real
# y no a la misma consulta repetida mil veces
MENSAJES = [
    "cuanto debo de mi boleta",
    "me cobraron dos veces el mes pasado",
    "no tengo internet desde anoche",
    "el router parpadea en rojo",
    "quiero cambiar mi plan a uno mas barato",
    "necesito agendar una visita tecnica",
    "a que hora llega el tecnico",
    "quiero dar de baja el servicio",
    "cuando se vence lo que tengo que pagar",
    "ando lento el wifi",
]


class Cliente(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):
        self.cabeceras = {"X-API-Key": os.getenv("API_KEY", "")}
        self.siguiente = itertools.cycle(MENSAJES).__next__

    @task
    def predecir(self):
        self.client.post("/api/predict", json={"texto": self.siguiente()},
                         headers=self.cabeceras, name="POST /api/predict")
