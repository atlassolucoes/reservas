#!/usr/bin/env python3
"""
Fetches data from Google Sheets and injects it as const DATA= into dashboard.html
"""

import os
import json
import re
from datetime import datetime

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    os.system("pip install gspread google-auth --quiet")
    import gspread
    from google.oauth2.service_account import Credentials

SHEET_ID = os.environ.get(
    "SHEET_ID",
    "1meO-CLIibr0L6osznnnYJXU8N7obiURP3-M56AwPvWs"
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def parse_date(val):
    if not val or str(val).strip() == "":
        return None
    val = str(val).strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(val, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


def parse_datetime(val):
    if not val or str(val).strip() == "":
        return None
    val = str(val).strip()
    for fmt in (
        "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M",
        "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M",
        "%d/%m/%Y", "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(val, fmt).strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            pass
    return None


def parse_num(val):
    if val is None or str(val).strip() == "":
        return None
    val = str(val).strip()
    val = re.sub(r"[R$\s]", "", val)
    if "," in val and "." in val:
        val = val.replace(".", "").replace(",", ".")
    elif "," in val:
        val = val.replace(",", ".")
    try:
        return float(val)
    except ValueError:
        return None


def parse_int(val):
    n = parse_num(val)
    return int(n) if n is not None else None


def rows_to_dicts(worksheet):
    rows = worksheet.get_all_values()
    if not rows:
        return []
    headers = [h.strip() for h in rows[0]]
    result = []
    for row in rows[1:]:
        if not any(c.strip() for c in row):
            continue
        padded = row + [""] * (len(headers) - len(row))
        result.append(dict(zip(headers, padded)))
    return result


def main():
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if creds_json:
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write(creds_json)
            creds_file = f.name
    else:
        creds_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")

    creds = Credentials.from_service_account_file(creds_file, scopes=SCOPES)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SHEET_ID)

    ws = sh.worksheet("RESERVAS")
    reservas = []
    for i, r in enumerate(rows_to_dicts(ws), start=1):
        guest = str(r.get("HOSPEDE", "")).strip()
        data_reserva = parse_date(r.get("DATA RESERVA", ""))
        if not guest and not data_reserva:
            continue
        reservas.append({
            "id": i,
            "platform": str(r.get("PLATAFORMA", "")).strip().upper(),
            "dataReserva": data_reserva,
            "guest": guest,
            "phone": str(r.get("TELEFONE", "")).strip(),
            "status": str(r.get("STATUS", "")).strip(),
            "people": parse_int(r.get("QUANTIDADE DE PESSOAS", "")),
            "days": parse_int(r.get("QUANTIDADE DE DIAS", "")),
            "room": str(r.get("QUARTO", "")).strip().upper(),
            "checkin": parse_datetime(r.get("CHECK-IN", "")),
            "checkout": parse_datetime(r.get("CHECK-OUT", "")),
            "value": parse_num(r.get("VALOR RESERVA", "")),
            "commission": parse_num(r.get("VALOR COMISSÃO", "")),
            "netValue": parse_num(r.get("VALOR A RECEBER", "")),
            "received": parse_date(r.get("DATA DO RECEBIMENTO", "")),
            "obs": str(r.get("OBSERVAÇÃO", "")).strip(),
        })

    payload = {
        "updated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "reservas": reservas,
    }

    json_str = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    html_path = os.path.join(os.path.dirname(__file__), "dashboard.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    new_data_line = f"const DATA = {json_str};"
    html = re.sub(
        r"const DATA\s*=\s*\{[^;]*\};",
        new_data_line,
        html,
        flags=re.DOTALL,
    )

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✓ Data injected: {len(reservas)} reservas.")
    print(f"  Updated at: {payload['updated_at']}")


if __name__ == "__main__":
    main()
