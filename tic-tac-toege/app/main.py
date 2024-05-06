# ruff: noqa: F401

from config import static_files, templates
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from game.manager import GameManager
from models import GameFullError

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", app=static_files, name="static")

game_manager: GameManager | None = None


@app.get("/")
async def root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", context={"request": request})


@app.get("/reset")
async def reset(request: Request) -> HTMLResponse:
    global game_manager  # noqa: PLW0603
    game_manager = None
    return templates.TemplateResponse("game.html", context={"request": request})


@app.websocket("/game")
async def game_server(websocket: WebSocket) -> None:
    global game_manager  # noqa: PLW0603
    if not game_manager:
        game_manager = GameManager()
    try:
        await game_manager.connect(websocket)
        await game_manager.run_game(websocket)
    except GameFullError as e:
        await websocket.send_json(e.response.json())
        await websocket.close()
    except WebSocketDisconnect:
        ...


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
