from fastapi import FastAPI

app = FastAPI(
    title="WhatsApp Commerce Bot",
    description="Backend for WhatsApp B2B Ordering System",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {
        "status": "running",
        "message": "WhatsApp Commerce Bot API is live 🚀"
    }