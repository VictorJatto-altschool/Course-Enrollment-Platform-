from pydantic import BaseModel


class MessageOut(BaseModel):
    message: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
