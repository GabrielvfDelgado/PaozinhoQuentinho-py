from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import app.models.user
import app.models.reservation
from app.core.database import init_db
from app.services.evolution_api import evolution_api
from app.webhooks.handler import handle_evolution_webhook

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await evolution_api.setup_webhook()
    yield

app = FastAPI(title="Pãozinho Quentinho API", lifespan=lifespan)

@app.post("/webhook/evolution")
async def evolution_webhook(request: Request):
    payload = await request.json()
    print(f"\n🔔 Webhook Recebido! Evento: {payload.get('event')}")
    await handle_evolution_webhook(payload)
    return {"status": "received"}

@app.get("/")
def health_check():
    return {"status": "ok", "app": "Pãozinho Quentinho"}
