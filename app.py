import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests

APP_NAME = os.getenv("APP_NAME", "SMART CHEAT")
PANEL_BASE_URL = os.getenv("GREEDPANEL_BASE_URL", "https://xrcheats.in")  # e.g. https://yourdomain.com/GreedPanel
if PANEL_BASE_URL.endswith("/"):
    PANEL_BASE_URL = PANEL_BASE_URL[:-1]

if not PANEL_BASE_URL:
    # Hard fail early so deployment is explicit.
    raise RuntimeError("Missing GREEDPANEL_BASE_URL env var")

app = FastAPI(title=APP_NAME)

templates = Jinja2Templates(directory="python_site/templates")
app.mount("/static", StaticFiles(directory="python_site/static"), name="static")


class CreateOrderIn(BaseModel):
    plan_id: str
    telegram_id: str


class VerifyPaymentIn(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


def panel_url(path: str) -> str:
    # Call existing GreedPanel PHP endpoints.
    return PANEL_BASE_URL + path


@app.get("/", response_class=HTMLResponse)
def store(request: Request, telegram_id: str = ""):
    # We can render plans directly using panel store HTML, but that’s not ideal.
    # For simplicity, render a store page that loads plans via JS from GreedPanel.
    return templates.TemplateResponse(
        "store.html",
        {
            "request": request,
            "app_name": APP_NAME,
            "telegram_id": telegram_id,
            "panel_base_url": PANEL_BASE_URL,
        },
    )


@app.get("/api/plans")
def plans():
    # Use GreedPanel store.php to render plans? Instead, read from DB is not possible from here.
    # Minimal approach: call the GreedPanel store.html and parse? Not robust.
    # Therefore, we expose a small JSON bridge by calling a dedicated API is not present.
    # As a practical implementation, we call GreedPanel webapp store.php? The response is HTML.
    # We'll return an error instructing you to add an API if you want dynamic plans.
    raise HTTPException(
        501,
        "plans endpoint not implemented. Add /api endpoint in GreedPanel or provide a static plans list.",
    )


@app.post("/api/pay/create-order")
def create_order(payload: CreateOrderIn):
    try:
        url = panel_url("/features/telegram/payments/create_order.php")
        resp = requests.post(url, json={"plan_id": payload.plan_id, "telegram_id": payload.telegram_id}, timeout=30)
        data = resp.json()
        if resp.status_code >= 400 or not data.get("success"):
            return JSONResponse(status_code=400, content=data)
        return data
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/api/pay/verify")
def verify_payment(payload: VerifyPaymentIn):
    try:
        url = panel_url("/features/telegram/payments/verify_payment.php")
        resp = requests.post(
            url,
            json={
                "razorpay_order_id": payload.razorpay_order_id,
                "razorpay_payment_id": payload.razorpay_payment_id,
                "razorpay_signature": payload.razorpay_signature,
            },
            timeout=30,
        )
        data = resp.json()
        if resp.status_code >= 400 or not data.get("success"):
            return JSONResponse(status_code=400, content=data)
        return data
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/keys", response_class=HTMLResponse)
def keys_page(request: Request, telegram_id: str = ""):
    if not telegram_id:
        # Also allow alternative query param name.
        telegram_id = request.query_params.get("tid", "")

    if not telegram_id:
        return templates.TemplateResponse(
            "keys.html",
            {
                "request": request,
                "app_name": APP_NAME,
                "telegram_id": "",
                "message": "Provide telegram_id in query. Example: /keys?telegram_id=123456" ,
            },
        )

    # Delegate rendering to GreedPanel webapp mykeys.php (already supports tid).
    return templates.TemplateResponse(
        "keys.html",
        {
            "request": request,
            "app_name": APP_NAME,
            "telegram_id": telegram_id,
            "message": "",
            "mykeys_url": panel_url(f"/features/telegram/webapp/mykeys.php?tid={telegram_id}"),
        },
    )


@app.get("/health")
def health():
    return {"ok": True, "panel_base_url": PANEL_BASE_URL}


