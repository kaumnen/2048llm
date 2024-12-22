from fastapi import APIRouter
from utils.llm.llm_handler import start_llm
from utils.llm.models import InitLLMModel

router = APIRouter()


@router.post("/start-llm")
async def init_llm_solve(llm_model: InitLLMModel):
    await start_llm(llm_model)
