import httpx
from app.core.config import settings

class EvolutionAPI:
    def __init__(self):
        self.base_url = settings.evolution_api_url
        self.instance = settings.evolution_api_instance
        self.headers = {
            "apikey": settings.evolution_api_key,
            "Content-Type": "application/json"
        }

    async def setup_webhook(self):
        url = f"{self.base_url}/webhook/set/{self.instance}"
        payload = {
            "url": "http://app:8000/webhook/evolution",
            "enabled": True,
            "events": ["MESSAGES_UPSERT", "MESSAGES_UPDATE"]
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=self.headers)
                if response.status_code == 200:
                    print(f"✅ Webhook configurado com sucesso")
                else:
                    print(f"⚠️ Falha ao configurar Webhook: {response.text}")
        except Exception as e:
            print(f"❌ Erro de conexão ao configurar Webhook: {e}")

evolution_api = EvolutionAPI()
