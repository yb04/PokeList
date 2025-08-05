import os

from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
import pandas as pd
import backend.pokemontcg_api
import backend.PokeList
import shutil


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

search_cache = []
MAX_CACHE_SIZE = 10
CARD_DF = pd.DataFrame()
CSV_PATH = "cards.csv"


@app.get("/", response_class=HTMLResponse)
async def search(request: Request, name: str = None):
    cards = []
    global CARD_DF
    if not name:
        return templates.TemplateResponse("index.html", {"request": request})
    if name:
        search_terms = name.split()
        df = backend.pokemontcg_api.get_cards(*search_terms)
        if df is not None and not df.empty:
            CARD_DF = df
            cards = df.to_dict(orient="records")
            if name not in search_cache:
                search_cache.insert(0, name)
                if len(search_cache) > MAX_CACHE_SIZE:
                    search_cache.pop()
        else:
            CARD_DF = pd.DataFrame()
    return templates.TemplateResponse("cards_results.html", {
        "request": request,
        "cards": cards,
        "recent": search_cache
    })


@app.get("/download")
async def download():
    global CARD_DF
    file_path = "export.csv"
    df = CARD_DF
    if (df is None or df.empty) and os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
    if df is not None and not df.empty:
        backend.PokeList.save_list(df, file_path)
        if os.path.exists(file_path):
            return FileResponse(path=file_path, filename="export.csv", media_type="text/csv")
        else:
            return HTMLResponse("Datei konnte nicht erstellt werden", status_code=500)
    return HTMLResponse("Keine Daten zum Download verfügbar", status_code=404)


@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        return {"error": "Nur CSV-Dateien erlaubt."}
    with open(CSV_PATH, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return RedirectResponse(url="/results", status_code=303)


@app.get("/card/{card_id}", response_class=HTMLResponse)
async def card_detail(request: Request, card_id: str):
    global CARD_DF
    df = CARD_DF
    if df.empty and os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
    if not df.empty:
        row = df[df["id"] == card_id]
        if not row.empty:
            card = row.iloc[0].to_dict()
            return templates.TemplateResponse("card.html", {"request": request, "card": card})
    return HTMLResponse("Karte nicht gefunden", status_code=404)


@app.get("/results", response_class=HTMLResponse)
async def show_results(request: Request):
    global CARD_DF
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
    else:
        df = pd.DataFrame(columns=["id", "owned"])
    if "owned" not in df.columns:
        df["owned"] = False
    CARD_DF = df
    owned_count = int(df["owned"].sum())
    missing_count = int(len(df) - owned_count)
    return templates.TemplateResponse("cards_results.html", {
        "request": request,
        "cards": df.to_dict(orient="records"),
        "count": len(df),
        "owned_count": owned_count,
        "missing_count": missing_count
    })


@app.post("/update_owned") #TODO: need to show last page and refresh for it to show, is working good, /update_owned opens in url (needs to be updated /results)
async def update_owned(request: Request):
    form = await request.form()
    global CARD_DF
    if CARD_DF is None or CARD_DF.empty:
        return RedirectResponse(url="/results", status_code=303)
    if "owned" not in CARD_DF.columns:
        CARD_DF["owned"] = False
    # Checkboxes übernehmen
    for idx, row in CARD_DF.iterrows():
        owned_key = f"owned_{row['id']}"
        CARD_DF.at[idx, "owned"] = owned_key in form
    # CSV sofort speichern
    CARD_DF.to_csv(CSV_PATH, index=False)
    return RedirectResponse(url="/results", status_code=200)