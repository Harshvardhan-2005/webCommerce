import httpx

from app.core.config import settings
from app.core.logger import logger


class WhatsAppClient:
    """
    Client responsible for communicating with the
    WhatsApp Cloud API.
    """

    def __init__(self):
        self.base_url = (
            f"https://graph.facebook.com/"
            f"{settings.WA_API_VERSION}/"
            f"{settings.WA_PHONE_NUMBER_ID}"
        )

        self.headers = {
            "Authorization": f"Bearer {settings.WA_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

    async def send_text_message(
        self,
        phone_number: str,
        message: str,
    ) -> dict:

        url = f"{self.base_url}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": message
            },
        }

        logger.info(f"Sending WhatsApp message to {phone_number}")

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                url,
                headers=self.headers,
                json=payload,
            )

        logger.info(f"Meta Status Code: {response.status_code}")

        response.raise_for_status()

        return response.json()


whatsapp_client = WhatsAppClient()