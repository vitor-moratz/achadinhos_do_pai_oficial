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
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    base = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
    try:
        if image_url:
            # Envia imagem sem caption
            resp = requests.post(f"{base}/sendPhoto", json={
                "chat_id": TELEGRAM_CHAT_ID,
                "photo":   image_url,
            }, timeout=10)
            if not resp.ok:
                logger.warning("Telegram sendPhoto failed: %s — %s", resp.status_code, resp.text)
        # Envia o texto separado
        resp = requests.post(f"{base}/sendMessage", json={
            "chat_id":                  TELEGRAM_CHAT_ID,
            "text":                     message,
            "parse_mode":               "Markdown",
            "disable_web_page_preview": False,
        }, timeout=10)
        if not resp.ok:
            logger.warning("Telegram sendMessage failed: %s — %s", resp.status_code, resp.text)
    except Exception as exc:
        logger.warning("Telegram notification error: %s", exc)


def _send_whatsapp(message: str, image_url: str = ""):
    """Envia imagem (sem caption) + texto separado via Z-API."""
    if not (ZAPI_INSTANCE_ID and ZAPI_TOKEN and ZAPI_PHONE):
        return

    base    = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}"
    headers = {"Content-Type": "application/json"}
    if ZAPI_CLIENT_TOKEN:
        headers["Client-Token"] = ZAPI_CLIENT_TOKEN

    try:
        if image_url:
            # Envia imagem com caption (texto junto)
            resp = requests.post(f"{base}/send-image", json={
                "phone":   ZAPI_PHONE,
                "image":   image_url,
                "caption": message,
            }, headers=headers, timeout=10)
        else:
            resp = requests.post(f"{base}/send-text", json={
                "phone":   ZAPI_PHONE,
                "message": message,
            }, headers=headers, timeout=10)
        if not resp.ok:
            logger.warning("WhatsApp send failed: %s — %s", resp.status_code, resp.text)
    except Exception as exc:
        logger.warning("WhatsApp (Z-API) notification error: %s", exc)


def notify_new_product(product: dict):
    """
    Dispara notificações de Telegram e WhatsApp em background thread,
    para não atrasar a resposta HTTP.
    """
    if not (TELEGRAM_BOT_TOKEN or (ZAPI_INSTANCE_ID and ZAPI_TOKEN and ZAPI_PHONE)):
        return

    message   = _build_message(product)
    image_url = product.get("image_url", "") or ""

    def _run():
        _send_telegram(message, image_url)
        _send_whatsapp(message, image_url)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
