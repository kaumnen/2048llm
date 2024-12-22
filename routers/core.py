from fastapi import APIRouter
from utils.basic_functions import initial_setup, current_state, next_move

router = APIRouter()


@router.get("/start-game")
async def start_game():
    session_id = await initial_setup()
    return {"session_id": session_id}


@router.post("/move")
async def move(session_id: str, direction: int):
    new_state = await next_move(session_id, direction)
    return {"game_state": new_state}


@router.get("/get-state")
async def get_scope(session_id: str, granularity: str = "full"):
    game_state = await current_state(session_id)

    return {"game_state": game_state[granularity]}
