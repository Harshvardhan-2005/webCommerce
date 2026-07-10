from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logger import logger
from app.services.auth_service import auth_service
from app.clients.whatsapp_client import WhatsAppClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application started successfully.")
    yield
    logger.info("Application shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


# Register all API routes
app.include_router(api_router)


@app.get("/")
async def root():
    logger.info("Health check endpoint called.")

    return {
        "status": "running",
        "application": settings.APP_NAME,
        "environment": settings.APP_ENV,
    }


@app.get("/debug")
async def debug():
    return {
        "verify_token": settings.WA_VERIFY_TOKEN,
        "environment": settings.APP_ENV,
    }


@app.get("/client-test")
async def client_test():
    from app.clients.whatsapp_client import whatsapp_client

    return {
        "base_url": whatsapp_client.base_url,
    }


whatsapp_client = WhatsAppClient()


@app.get("/send-test")
async def send_test():
    response = await whatsapp_client.send_text_message(
        phone_number="918588902062",
        message="Hello from FastAPI 🚀",
    )

    return response


@app.get("/test-magento-auth")
async def test_magento_auth():
    result = await auth_service.authenticate_salesman()

    return {
        "status": "success",
        "admin": result["admin"],
    }


@app.get("/debug-magento")
async def debug_magento():
    return {
        "magento_url": settings.MAGENTO_URL,
    }