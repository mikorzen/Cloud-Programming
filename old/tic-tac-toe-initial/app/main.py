# ruff: noqa: F401, ERA001

from configuration import static_files, templates
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from logic.manager import GameFullError, GameManager, GameOver, InvalidMoveError

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
async def game(websocket: WebSocket) -> None:
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
    except InvalidMoveError as e:
        await websocket.send_json({"error": str(e)})
    except GameOver:
        await websocket.close()
    except WebSocketDisconnect:
        ...


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8080)  # noqa: S104
