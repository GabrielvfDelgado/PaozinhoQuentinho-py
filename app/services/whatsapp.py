import httpx
import asyncio
from app.core.config import settings

class WhatsAppService:
    def __init__(self):
        self.base_url = settings.evolution_api_url
        self.instance = settings.evolution_api_instance
        self.apikey = settings.evolution_api_key
        self.headers = {
            "apikey": self.apikey,
            "Content-Type": "application/json"
        }

    async def send_text(self, number: str, text: str, force_admin: bool = False, quoted: dict = None):
        url = f"{self.base_url}/message/sendText/{self.instance}"
        recipient = settings.admin_phone if force_admin else number
        payload = {
            "number": recipient,
            "textMessage": {"text": text}
        }
        if quoted:
            payload["quoted"] = quoted

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=self.headers)
                if response.status_code not in [200, 201]:
                    print(f"Erro no envio para {recipient}: {response.text}")
                return response
            except Exception as e:
                print(f"Erro ao enviar: {e}")
                return None

    async def send_admin_menu(self, number: str, force_admin: bool = False):
        menu_text = (
            "🛠️ *PAINEL ADMINISTRATIVO*\n\n"
            "1️⃣ *Disparar Pão Francês*\n"
            "2️⃣ *Disparar Pão de Queijo*\n"
            "3️⃣ *Ver Reservas de Hoje*\n"
            "4️⃣ *Ver Clientes Ativos*\n"
            "5️⃣ *Cadastrar Novo Cliente*\n"
            "6️⃣ *Remover Cliente*\n"
            "7️⃣ *Limpar Reservas de Hoje*\n\n"
            "--- Paozinho Quentinho ---"
        )
        return await self.send_text(number, menu_text, force_admin=force_admin)

whatsapp_service = WhatsAppService()
