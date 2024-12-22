from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers.core import router as core_router
from routers.llm import router as llm_router


app = FastAPI()

app.mount("/static", StaticFiles(directory="./2048"), name="static")


@app.get("/", tags=["default"])
async def show_game():
    return FileResponse("./2048/index.html")


app.include_router(core_router, prefix="/core", tags=["CORE"])
app.include_router(llm_router, prefix="/llm", tags=["LLM"])
