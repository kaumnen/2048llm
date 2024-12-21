from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from playwright.async_api import async_playwright, Browser, Page
import uuid
import os
import json
from openai import OpenAI
from loguru import logger

active_games: dict[str, tuple[Browser, Page]] = {}


async def initial_setup():
    playwright = await async_playwright().start()
    chromium = playwright.chromium
    browser = await chromium.launch(headless=False, args=["--start-maximized"])
    page = await browser.new_page()
    await page.set_viewport_size({"width": 800, "height": 1000})
    await page.goto("http://localhost:8000")
    await page.wait_for_load_state("networkidle")

    await page.evaluate(
        "var gameManager = new GameManager(4,KeyboardInputManager,HTMLActuator,LocalStorageManager);"
    )

    session_id = str(uuid.uuid4())
    active_games[session_id] = (browser, page)
    return session_id


async def current_state(session_id):
    if session_id not in active_games:
        raise HTTPException(
            status_code=404, detail="Session not found. Start a game first."
        )

    _, page = active_games[session_id]

    game_state = await page.evaluate("JSON.stringify(gameManager.serialize())")
    game_over = json.loads(game_state)["over"]
    game_score = json.loads(game_state)["score"]
    game_won = json.loads(game_state)["won"]
    game_table_state = await page.evaluate("""
            var gameState = JSON.stringify(gameManager.serialize());
            const parsedState = JSON.parse(gameState);

            const gridSize = parsedState.grid.size;
            const cells = parsedState.grid.cells;

            const grid = Array(gridSize).fill(null).map(() => Array(gridSize).fill('x'));

            for (let row = 0; row < cells.length; row++) {
                for (let col = 0; col < cells[row].length; col++) {
                    const cell = cells[row][col];
                    if (cell) {
                        grid[cell.position.y][cell.position.x] = cell.value
                    }
                }
            }

            const gridString = JSON.stringify(grid);

            gridString;
        """)

    logger.debug(f"Game state: {game_state}")
    logger.debug(f"Game table state: {game_table_state}")
    logger.debug(f"Game over: {game_over}")
    logger.debug(f"Game score: {game_score}")
    logger.debug(f"Game won: {game_won}")
    return {
        "full": json.loads(game_state),
        "table": json.loads(game_table_state),
        "over": game_over,
        "score": game_score,
        "won": game_won,
    }


async def next_move(session_id, direction):
    if session_id not in active_games:
        raise HTTPException(
            status_code=404, detail="Session not found. Start a game first."
        )

    _, page = active_games[session_id]

    await page.evaluate(f"gameManager.move({direction})")

    game_state = await current_state(session_id)

    return game_state
