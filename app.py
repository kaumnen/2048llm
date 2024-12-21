from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uuid

from playwright.async_api import async_playwright, Browser, Page

app = FastAPI()

app.mount("/static", StaticFiles(directory="./2048"), name="static")

active_games: dict[str, tuple[Browser, Page]] = {}


@app.get("/")
async def show_game():
    return FileResponse("./2048/index.html")


@app.get("/start-game")
async def start_game():
    playwright = await async_playwright().start()
    chromium = playwright.chromium
    browser = await chromium.launch(headless=False, args=["--start-maximized"])
    page = await browser.new_page()
    await page.set_viewport_size({"width": 800, "height": 1200})
    await page.goto("http://localhost:8000")
    await page.wait_for_load_state("networkidle")

    await page.evaluate(
        "var gameManager = new GameManager(4,KeyboardInputManager,HTMLActuator,LocalStorageManager);"
    )

    session_id = str(uuid.uuid4())
    active_games[session_id] = (browser, page)
    return {"session_id": session_id}


@app.post("/move")
async def move(session_id: str, direction: int):
    if session_id not in active_games:
        raise HTTPException(
            status_code=404, detail="Session not found. Start a game first."
        )

    _, page = active_games[session_id]

    await page.evaluate(f"gameManager.move({direction})")

    game_state = await page.evaluate("JSON.stringify(gameManager.serialize())")

    return {"game_state": game_state}


@app.get("/get-state")
async def get_scope(session_id: str):
    if session_id not in active_games:
        raise HTTPException(
            status_code=404, detail="Session not found. Start a game first."
        )

    _, page = active_games[session_id]

    game_state = await page.evaluate("JSON.stringify(gameManager.serialize())")

    return {"game_state": game_state}
