from typing import List, Optional

from pydantic import BaseModel, Field


class TextMessage(BaseModel):
    body: str


class Message(BaseModel):
    from_: str = Field(alias="from")
    id: str
    type: str
    text: Optional[TextMessage] = None

    model_config = {
        "populate_by_name": True
    }


class Value(BaseModel):
    messages: List[Message] = []


class Change(BaseModel):
    value: Value


class Entry(BaseModel):
    changes: List[Change]


class WhatsAppWebhook(BaseModel):
    entry: List[Entry]