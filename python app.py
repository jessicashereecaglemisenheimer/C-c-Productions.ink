#!/usr/bin/env python3
"""Local savings-account and ACH-fun DEMO
Run: python My_Money.py, then open http://localhost:8000
This demo does NOT hold money or connect to a real ACH network.
"""
from __future__ import annotations
import hashlib, hmac, html, json, os
from contextlib import closing
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DATA_FILE = Path("my_money.json")
BALANCE_START = Decimal("8300000.00")
DAILY_PROFIT = Decimal("10375.00")

def load_ledger():
    if DATA_FILE.exists():
        try:
            d = json.loads(DATA_FILE.read_text())
            return Decimal(d["principal"]), Decimal(d["daily"])
        except (ValueError, KeyError, json.JSONDecodeError):
            pass
    return BALANCE_START, DAILY_PROFIT

def save_ledger(principal, daily):
    DATA_FILE.write_text(json.dumps({
        "principal": str(principal),
        "daily": str(daily),
        "updated": datetime.now(timezone.utc).isoformat()
    }))

principal, daily = load_ledger()

class Handler(BaseHTTPRequestHandler):
    def send_page(self, title, body, code=200):
        self.send_response(code)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        page = f"<html><head><title>{html.escape(title)}</title></head><body>{body}</body></html>"
        self.wfile.write(page.encode())

    def do_GET(self):
        try:
            path = urlparse(self.path).path
            if path == "/":
                body = f"""
                <h1>Beakkoame Bank - Local Vault</h1>
                <div class='card'>Principal: ${principal:,.2f}</div>
                <div class='card'>Daily Profit: ${daily:,.2f}</div>
                <div class='card'>Annual Yield: 45.61% | Liquidity: SECURE</div>
                <hr>
                <p><b>Demo only - No real ACH</b></p>
                <a class='button' href='/'>Refresh</a>
                """
                self.send_page("Vault", body)
            else:
                self.send_page("Not Found", "<h1>Not Found</h1>", 404)

        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            self.send_page(
                "Error",
                f"<h1>Could not continue</h1><div class='card error'>{html.escape(str(exc))}</div><a class='button' href='/'>Back</a>",
                400
            )

    def log_message(self, *args):
        return

if __name__ == "__main__":
    print(f"Beakkoame Bank Local Vault LIVE")
    print(f"Principal ${principal:,.2f} | Daily ${daily:,.2f}")
    print("Open http://localhost:8000")
    save_ledger(principal, daily)
    HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
