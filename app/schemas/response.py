from typing import Optional

from pydantic import BaseModel


class WebhookResponse(BaseModel):
    status: str
    sender: Optional[str] = None
    message_type: Optional[str] = None