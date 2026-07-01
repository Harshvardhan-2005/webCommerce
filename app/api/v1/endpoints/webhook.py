from fastapi import APIRouter, HTTPException, Query
from fastapi import Request
from app.services.conversation_service import conversation_service
from app.core.config import settings
from app.core.logger import logger
from app.schemas.webhook import WhatsAppWebhook

router = APIRouter(
    prefix="/webhook",
    tags=["WhatsApp Webhook"],
)


@router.get("")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
):
    logger.info("Webhook verification request received.")

    if hub_mode != "subscribe":
        logger.warning("Invalid hub.mode received.")
        raise HTTPException(status_code=400, detail="Invalid mode")

    if hub_verify_token != settings.WA_VERIFY_TOKEN:
        logger.warning("Invalid verify token.")
        raise HTTPException(status_code=403, detail="Verification failed")

    logger.info("Webhook verified successfully.")

    return int(hub_challenge)




@router.post("")
async def receive_webhook(request: Request):
    body = await request.json()

    logger.info("=" * 80)
    logger.info(body)
    logger.info("=" * 80)

    return {"status": "received"}