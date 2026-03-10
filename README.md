# Ninja Webhook Relay

FastAPI service that receives a webhook payload (e.g. from TraderPost), forwards it to Discord, and submits the order to TraderPost via its webhook URL (no API key; the URL is the secret).

## TraderPost webhook

TraderPost sends webhooks to a URL you configure. Their webhook URLs look like:

```
https://webhooks.traderspost.io/trading/webhook/{webhook-id}/{token}
```

Deploy this app and set your **outgoing** webhook URL in TraderPost to your service:

- **Webhook URL:** `https://<your-deployed-app>/webhook`

TraderPost will POST to that URL; this app forwards the payload to Discord and sends the order to TraderPost by POSTing to your TraderPost webhook URL.

## Behavior

- Receives `POST /webhook`.
- Forwards the incoming payload to `DISCORD_WEBHOOK_URL`.
- Parses `content` as JSON to build a TraderPost order.
- Sends the order to TraderPost by POSTing to `TRADERPOST_WEBHOOK_URL` (no API key).
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
- `TRADERPOST_WEBHOOK_URL` (e.g. `https://webhooks.traderspost.io/trading/webhook/{id}/{token}`)
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

## Deploy with Coolify (Nixpacks)

1. In Coolify, create a new **Application** and connect this repo (GitHub/GitLab or public URL).
2. Set **Build Pack** to **Nixpacks**. The repo includes a `nixpacks.toml` that runs:
   - `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`
3. **Port**: Set **Port Exposes** to `8000` (or the port your stack uses; Coolify may set `PORT` for you).
4. **Environment**: Add the same variables as in `.env.example`:
   - `DISCORD_WEBHOOK_URL`
   - `TRADERPOST_WEBHOOK_URL`
   - Optionally `REQUEST_TIMEOUT_SECONDS`, `LOG_LEVEL`
5. Deploy. Your webhook URL will be `https://<your-coolify-domain>/webhook` — use that in TraderPost as the destination.
