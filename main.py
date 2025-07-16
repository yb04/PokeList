from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
import pandas as pd
import backend.pokemontcg_api

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

CARD_DF: pd.DataFrame = pd.DataFrame()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, name: str = ""):
    global CARD_DF
    cards = []
    count = 0
    if name:
        CARD_DF = backend.pokemontcg_api.get_cards(name)
        if not CARD_DF.empty:
            cards = CARD_DF.to_dict("records")
            count = len(cards)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "cards": cards,
        "count": count
    })


@app.get("/card/{card_id}", response_class=HTMLResponse)
async def card_detail(request: Request, card_id: str):
    global CARD_DF
    if not CARD_DF.empty:
        row = CARD_DF[CARD_DF["id"] == card_id]
        if not row.empty:
            card = row.iloc[0].to_dict()
            return templates.TemplateResponse("card.html", {"request": request, "card": card})
    return HTMLResponse("Karte nicht gefunden", status_code=404)
