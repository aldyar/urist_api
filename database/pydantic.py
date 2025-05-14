from pydantic import BaseModel

class ChatRequest(BaseModel):
    chat_id: int
    question: str