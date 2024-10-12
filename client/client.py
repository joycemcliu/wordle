import os

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

app = FastAPI()


@app.get("/health")
async def health():
    return


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        context={
            "request": request,
            "server_port": os.environ.get("SERVER_PORT", 8010),
            "client_port": 8011,
        },
    )


if __name__ == "__main__":
    realod = os.environ.get("ENV", "dev") == "dev"
    uvicorn.run("client:app", host="0.0.0.0", port=8011, reload=realod)
