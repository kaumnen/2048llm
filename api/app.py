from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="./2048"), name="static")


@app.get("/")
async def show_game():
    return FileResponse("./2048/index.html")
