from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from backend.pokemontcg_api import get_cards
import pandas as pd

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request, name: str = ""):
    cards = []
    if name:
        tokens = [x.strip() for x in name.replace(",", " ").split()] # Split input by comma or space
        df: pd.DataFrame = get_cards(*tokens)
        if df is not None and not df.empty:
            df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
            df["release_date"] = df["release_date"].dt.strftime("%Y-%m-%d")
            df = df.sort_values(by=["release_date", "id"], ascending=True)
            cards = df.to_dict(orient="records")
    return templates.TemplateResponse("index.html", {"request": request, "cards": cards})