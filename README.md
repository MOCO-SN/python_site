# Python + HTML payment + key site (GreedPanel reuse)

This site provides a **public Store + Keys** UI and reuses your existing GreedPanel PHP payment/key system.

## What it does
- **GET /** : Store page (you must configure plans list in `templates/store.html` for now)
- **POST /api/pay/create-order** : calls GreedPanel `/features/telegram/payments/create_order.php`
- **POST /api/pay/verify** : calls GreedPanel `/features/telegram/payments/verify_payment.php`
- **GET /keys?telegram_id=...** : embeds GreedPanel `/features/telegram/webapp/mykeys.php?tid=...`

## Prerequisites
- GreedPanel is installed and running (PHP).
- Razorpay is configured in GreedPanel.

## Configure
Create `.env` or set env var directly:

- `GREEDPANEL_BASE_URL` = full URL to your GreedPanel folder
  - Example: `https://example.com/GreedPanel`

## Run
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

set GREEDPANEL_BASE_URL=https://example.com/GreedPanel
uvicorn app:app --reload --port 8000
```

Then open:
- http://localhost:8000/

## Important notes
- Buyer must enter the **same `telegram_id`** used in your Telegram webapp flow, because GreedPanel payment endpoints require `telegram_id`.
- Plans list is currently a placeholder in `templates/store.html` (`plansList`).
  - Replace with your real plan IDs/names/prices or ask to implement a proper `/api/plans` bridge.

