# ruff: noqa: F401

import json
from typing import Any

import requests
from config import static_files, templates
from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from game.manager import GameManager
from joserfc.errors import ExpiredTokenError
from joserfc.jwk import KeySet
from joserfc.jwt import JWTClaimsRegistry, Token, decode
from models import GameFullError
from starlette.middleware.sessions import SessionMiddleware

GRANT_TYPE_CODE = "authorization_code"
GRANT_TYPE_REFRESH = "refresh_token"
CLIENT_ID = "53v0am9k2tme1vkrvv759a7rke"

REDIRECT_URI = "http://localhost:8080/login"
KEY_URI = "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_jK2QTRvFn/.well-known/jwks.json"
TOKEN_URI = "https://ttt-game.auth.us-east-1.amazoncognito.com/oauth2/token"  # noqa: S105

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key="secret",  # noqa: S106
    max_age=None,
)
app.mount("/static", app=static_files, name="static")

key_set: KeySet | None = None
claim_registry: JWTClaimsRegistry = JWTClaimsRegistry()

game_manager: GameManager | None = None


class NotAuthenticatedError(Exception): ...


def get_token_data(code: str) -> dict[str, Any]:
    request_data = {
        "grant_type": GRANT_TYPE_CODE,
        "client_id": CLIENT_ID,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    response = requests.post(  # noqa: S113
        TOKEN_URI,
        data=request_data,
    )
    return response.json()


def get_tokens(request: Request) -> tuple[str | None, str | None]:
    access_token = request.session.get("access_token")
    refresh_token = request.session.get("refresh_token")
    return access_token, refresh_token


def validate_token(request: Request) -> Token:
    access_token, refresh_token = get_tokens(request)
    global key_set  # noqa: PLW0603
    if not key_set:
        response = requests.get(KEY_URI)  # noqa: S113
        key_set = KeySet.import_key_set(response.json())
    if not access_token:
        raise NotAuthenticatedError
    token = decode(access_token, key_set)  # type: ignore[arg-type]
    try:
        claim_registry.validate_exp(token.claims["exp"])
    except ExpiredTokenError:
        renew_token(request, refresh_token)
    return token


def renew_token(request: Request, refresh_token: str | None) -> None:
    if not refresh_token:
        raise NotAuthenticatedError
    request_data = {
        "grant_type": GRANT_TYPE_REFRESH,
        "client_id": CLIENT_ID,
        "refresh_token": refresh_token,
    }
    response = requests.post(  # noqa: S113
        TOKEN_URI,
        data=request_data,
    ).json()
    request.session["access_token"] = response.get("access_token")


def show_dialog_headers(title: str, message: str) -> dict[str, Any]:
    header_data = {
        "showDialog": {
            "title": title,
            "message": message,
        },
    }
    return {"Hx-Trigger": json.dumps(header_data)}


@app.get("/")
async def root(request: Request) -> HTMLResponse:
    context = {}
    try:
        token = validate_token(request)
        context.update({"username": token.claims.get("username")})
    except NotAuthenticatedError:
        ...
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context,
    )


@app.get("/login")
async def login(request: Request) -> HTMLResponse:
    code = request.query_params.get("code")
    if code and not get_tokens(request)[0]:
        token_data = get_token_data(code)
        request.session["access_token"] = token_data.get("access_token")
        request.session["refresh_token"] = token_data.get("refresh_token")
    token: Token = validate_token(request)  # type: ignore[arg-type]
    context = {"username": token.claims.get("username")}
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context,
    )


@app.get("/logout")
async def logout(request: Request) -> HTMLResponse:
    request.session.clear()
    global game_manager  # noqa: PLW0603
    game_manager = None
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/reset")
async def reset(request: Request) -> Response:
    context = {}
    try:
        token = validate_token(request)
        context.update({"username": token.claims.get("username")})
    except NotAuthenticatedError:
        headers = show_dialog_headers(
            "Not logged in",
            "You need to log in to be able to play.",
        )
        return Response(status_code=401, headers=headers)
    global game_manager  # noqa: PLW0603
    game_manager = None
    return templates.TemplateResponse(
        request=request,
        name="game.html",
        context=context,
    )


@app.get("/game")
async def game(request: Request) -> Response:
    context = {}
    try:
        token = validate_token(request)
        context.update({"username": token.claims.get("username")})
    except NotAuthenticatedError:
        headers = show_dialog_headers(
            "Not logged in",
            "You need to log in to be able to play.",
        )
        return Response(status_code=401, headers=headers)
    else:
        return templates.TemplateResponse(
            request=request,
            name="game.html",
            context=context,
        )


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

    uvicorn.run("main:app", host="localhost", port=8080)
