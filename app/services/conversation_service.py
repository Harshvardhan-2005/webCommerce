from app.clients.whatsapp_client import whatsapp_client
from app.core.logger import logger
from app.schemas.response import WebhookResponse
from app.schemas.webhook import WhatsAppWebhook


class ConversationService:
    """
    Handles all business logic related to incoming WhatsApp conversations.

    Responsibilities:
    - Parse webhook payload
    - Extract message details
    - Log conversation
    - Send WhatsApp reply
    - (Future) Detect intent
    - (Future) Manage session
    - (Future) Call Magento
    - (Future) Call Ollama
    """

    async def process_webhook(
        self,
        payload: WhatsAppWebhook,
    ) -> WebhookResponse:

        logger.info("Processing incoming WhatsApp webhook.")

        if not payload.entry:
            logger.info("No entry found in webhook payload.")
            return WebhookResponse(status="ignored")

        entry = payload.entry[0]

        if not entry.changes:
            logger.info("No changes found in webhook payload.")
            return WebhookResponse(status="ignored")

        change = entry.changes[0]

        if not change.value.messages:
            logger.info("No messages found in webhook payload.")
            return WebhookResponse(status="ignored")

        message = change.value.messages[0]

        logger.info("=" * 50)
        logger.info("New WhatsApp Message Received")
        logger.info("=" * 50)

        logger.info(f"Sender       : {message.from_}")
        logger.info(f"Message ID   : {message.id}")
        logger.info(f"Message Type : {message.type}")

        if message.text:
            logger.info(f"Message Text : {message.text.body}")

        logger.info("=" * 50)

        # Ignore non-text messages
        if message.type != "text":
            logger.info("Non-text message received. Ignoring.")

            return WebhookResponse(
                status="ignored",
                sender=message.from_,
                message_type=message.type,
            )

        # Send automatic reply
        try:
            response = await whatsapp_client.send_text_message(
                phone_number=message.from_,
                message="Hello! 👋 I received your message successfully."
            )

            logger.info("Reply sent successfully.")
            logger.info(response)

        except Exception:
            logger.exception("Failed to send WhatsApp reply.")

        return WebhookResponse(
            status="received",
            sender=message.from_,
            message_type=message.type,
        )


conversation_service = ConversationService()