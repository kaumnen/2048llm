from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from utils.core import initial_setup, current_state, next_move
from utils.llm import start_llm

app = FastAPI()


app.mount("/static", StaticFiles(directory="./2048"), name="static")


@app.get("/")
async def show_game():
    return FileResponse("./2048/index.html")


@app.get("/start-game")
async def start_game():
    session_id = await initial_setup()
    return {"session_id": session_id}


@app.post("/move")
async def move(session_id: str, direction: int):
    new_state = await next_move(session_id, direction)
    return {"game_state": new_state}


@app.get("/get-state")
async def get_scope(session_id: str, granularity: str = "full"):
    game_state = await current_state(session_id)

    return {"game_state": game_state[granularity]}


@app.post("/start-llm")
async def init_llm_solve(session_id: str):
    await start_llm(session_id)
