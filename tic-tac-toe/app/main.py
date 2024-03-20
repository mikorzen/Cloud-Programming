# ruff: noqa: F401, ERA001

from pathlib import Path

from configuration import templates
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from logic.manager import GameFullError, GameManager, GameOver, InvalidMoveError
from logic.tictactoe import Draw

_STATIC_DIR = Path(__file__).resolve().parents[1] / "static"
static_files = StaticFiles(directory=_STATIC_DIR)

app = FastAPI()
app.mount("/static", app=static_files, name="static")

game_manager: GameManager | None = None


@app.get("/")
async def root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("base.html", context={"request": request})


@app.get("/reset")
async def reset(request: Request) -> HTMLResponse:
    global game_manager  # noqa: PLW0603
    game_manager = None
    return templates.TemplateResponse(
        "pages/_tictactoe.html",
        context={"request": request},
    )


@app.websocket("/game")
async def websocket_endpoint(websocket: WebSocket) -> None:
    global game_manager  # noqa: PLW0603
    if not game_manager:
        game_manager = GameManager()
    try:
        await game_manager.connect(websocket)
    except GameFullError as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()
        return

    try:
        await game_manager.run_game(websocket)
    except Draw as e:
        await websocket.send_json({"error": str(e)})
    except InvalidMoveError as e:
        await websocket.send_json({"error": str(e)})
    except GameOver:
        await websocket.close()
    except WebSocketDisconnect:
        ...


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)  # noqa: S104
