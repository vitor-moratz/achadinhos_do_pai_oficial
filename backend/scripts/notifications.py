"""
Notification helpers — Telegram Bot + WhatsApp via Z-API.

Configure via environment variables:
  TELEGRAM_BOT_TOKEN  — token do bot (@BotFather)
  TELEGRAM_CHAT_ID    — ID do canal/grupo (ex: -1001234567890)
  ZAPI_INSTANCE_ID    — ID da instância Z-API
  ZAPI_TOKEN          — Token da instância Z-API
  ZAPI_CLIENT_TOKEN   — Client-Token de segurança (painel Z-API, opcional)
  ZAPI_PHONE          — Número ou ID do grupo (ex: 120363xxxxxxxxxx-group@g.us)
  SITE_URL            — URL pública do site (ex: https://seusite.com.br)
"""

import os
import logging
import threading
import requests

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")
ZAPI_INSTANCE_ID   = os.getenv("ZAPI_INSTANCE_ID", "")
ZAPI_TOKEN         = os.getenv("ZAPI_TOKEN", "")
ZAPI_CLIENT_TOKEN  = os.getenv("ZAPI_CLIENT_TOKEN", "")
ZAPI_PHONE         = os.getenv("ZAPI_PHONE", "")
SITE_URL           = os.getenv("SITE_URL", "").rstrip("/")


def _format_price(value):
    """Formata um número como preço brasileiro: R$ 1.234,56"""
    try:
        return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return str(value)


def _build_message(product: dict) -> str:
    title      = product.get("title", "Novo produto")
    price_from = product.get("price_from") or product.get("promo_price")
    price_to   = product.get("price_to")
    link       = product.get("affiliate_link", "")
    segment    = product.get("segment", "")
    category   = product.get("category", "")
    product_id = str(product.get("_id", ""))

    # Linha de preço
    if price_from and price_to:
        price_line = f"💰 *{_format_price(price_from)} – {_format_price(price_to)}*"
    elif price_from:
        price_line = f"💰 *{_format_price(price_from)}*"
    else:
        price_line = ""

    # Categoria
    meta_parts = [p for p in [segment, category] if p]
    meta_line  = f"📂 {' › '.join(meta_parts)}" if meta_parts else ""

    # Links
    product_url = f"{SITE_URL}/produto/{product_id}" if SITE_URL and product_id else ""

    lines = [
        "🔥 *NOVO ACHADO DO PAI!*",
        "",
        f"📦 *{title}*",
        "",
        price_line,
        meta_line,
        "",
        "✅ Selecionado e aprovado pelo Pai",
        "✅ Melhor preço da Shopee",
        "",
    ]

    if product_url:
        lines.append(f"👀 Ver detalhes: {product_url}")
    if link:
        lines.append(f"🛒 Comprar na Shopee: {link}")

    return "\n".join(line for line in lines if line is not None)


def _send_telegram(message: str, image_url: str = ""):
    token   = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return
    base = f"https://api.telegram.org/bot{token}"
    if image_url:
        try:
            resp = requests.post(f"{base}/sendPhoto", json={
                "chat_id": chat_id,
                "photo":   image_url,
            }, timeout=10)
            if not resp.ok:
                print(f"[notify] Telegram sendPhoto failed: {resp.status_code} — {resp.text}", flush=True)
        except Exception as exc:
            print(f"[notify] Telegram sendPhoto error: {exc}", flush=True)
    try:
        resp = requests.post(f"{base}/sendMessage", json={
            "chat_id":                  chat_id,
            "text":                     message,
            "parse_mode":               "Markdown",
            "disable_web_page_preview": False,
        }, timeout=10)
        if not resp.ok:
            print(f"[notify] Telegram sendMessage failed: {resp.status_code} — {resp.text}", flush=True)
        else:
            print("[notify] Telegram OK", flush=True)
    except Exception as exc:
        print(f"[notify] Telegram sendMessage error: {exc}", flush=True)


def _send_whatsapp(message: str, image_url: str = ""):
    instance     = os.getenv("ZAPI_INSTANCE_ID", "")
    token        = os.getenv("ZAPI_TOKEN", "")
    client_token = os.getenv("ZAPI_CLIENT_TOKEN", "")
    phone        = os.getenv("ZAPI_PHONE", "")
    if not (instance and token and phone):
        return

    base    = f"https://api.z-api.io/instances/{instance}/token/{token}"
    headers = {"Content-Type": "application/json"}
    if client_token:
        headers["Client-Token"] = client_token

    try:
        if image_url:
            resp = requests.post(f"{base}/send-image", json={
                "phone":   phone,
                "image":   image_url,
                "caption": message,
            }, headers=headers, timeout=10)
        else:
            resp = requests.post(f"{base}/send-text", json={
                "phone":   phone,
                "message": message,
            }, headers=headers, timeout=10)
        if not resp.ok:
            print(f"[notify] WhatsApp failed: {resp.status_code} — {resp.text}", flush=True)
        else:
            print("[notify] WhatsApp OK", flush=True)
    except Exception as exc:
        print(f"[notify] WhatsApp error: {exc}", flush=True)


def notify_new_product(product: dict):
    """Dispara notificações em background thread para não atrasar a resposta HTTP."""
    if not (os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("ZAPI_INSTANCE_ID")):
        return

    message   = _build_message(product)
    image_url = product.get("image_url", "") or ""

    def _run():
        _send_telegram(message, image_url)
        _send_whatsapp(message, image_url)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
