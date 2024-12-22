from fastapi import APIRouter
from utils.llm_handler import start_llm

router = APIRouter()


@router.post("/start-llm")
async def init_llm_solve(session_id: str):
    await start_llm(session_id)
