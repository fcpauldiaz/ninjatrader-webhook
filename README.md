# Ninja Webhook Relay

FastAPI service that receives a webhook payload, forwards it to Discord, and submits an order to TraderPost.

## Behavior

- Receives `POST /webhook`.
- Forwards the incoming payload to `DISCORD_WEBHOOK_URL`.
- Parses `content` as JSON to build a TraderPost order.
- Sends the order to TraderPost with bearer auth.
- Returns combined status for Discord and TraderPost:
  - `200` if both succeed
  - `207` if one succeeds
  - `502` if both fail

## Payload Contract

Incoming payload must be Discord-compatible and include a `content` string containing JSON order data.

Example logical payload:

```json
{
  "content": "{\"symbol\":\"AAPL\",\"side\":\"buy\",\"quantity\":1,\"order_type\":\"market\"}",
  "embeds": [
    {
      "title": "New order",
      "description": "Forwarded from source system"
    }
  ]
}
```

## Environment Variables

Copy `.env.example` to `.env` and set values:

- `DISCORD_WEBHOOK_URL`
- `TRADERPOST_API_KEY`
- `TRADERPOST_BASE_URL` (default: `https://api.traderpost.io`)
- `TRADERPOST_ORDERS_PATH` (default: `/v1/orders`)
- `REQUEST_TIMEOUT_SECONDS` (default: `10`)
- `LOG_LEVEL` (default: `INFO`)

## Install and Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Quick Test

```bash
curl -X POST "http://127.0.0.1:8000/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "content":"{\"symbol\":\"AAPL\",\"side\":\"buy\",\"quantity\":1,\"order_type\":\"market\",\"time_in_force\":\"day\"}",
    "embeds":[{"title":"Order Signal","description":"Sending to Discord and TraderPost"}]
  }'
```

## Health Check

```bash
curl "http://127.0.0.1:8000/health"
```
