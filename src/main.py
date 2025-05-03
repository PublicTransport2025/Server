import logging
import secrets
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from src.api import api_router
from src.core.constants import LOCALHOST_IP, PORT
from src.web import web_router

localhost_ip = LOCALHOST_IP
port = PORT

secret_file_path = Path(".flask_secret")
secret_key = None
try:
    with secret_file_path.open("r") as secret_file:
        secret_key = secret_file.read()
except FileNotFoundError:
    # Let's create a cryptographically secure code in that file
    with secret_file_path.open("w") as secret_file:
        secret_key = secrets.token_hex(32)
        secret_file.write(secret_key)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=secret_key)
app.include_router(api_router)
app.include_router(web_router)

logging.basicConfig(
    filename='errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a',
    encoding='utf-8'
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def integrity_exception_handler(request: Request, exc: RequestValidationError):
    info = await request.body()
    logging.error(info)
    return JSONResponse(
        status_code=422,
        content={"message": "Проверьте правильность ввода и заполненность всех полей"}
    )


@app.get("/")
async def ping():
    return RedirectResponse("/web/profile/login")


if __name__ == '__main__':
    uvicorn.run(app, host=localhost_ip, port=port)
