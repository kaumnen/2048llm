from pydantic import BaseModel


class InitLLMModel(BaseModel):
    session_id: str
    base_url: str
    api_key: str
    model: str
    prompt: str | None = None
    repeat_concatenation: str | None = None
