#!/usr/bin/env python3
import os
import json
import time
import requests
from typing import Dict, Any, List, Iterable, Tuple, Optional

URL = "https://stageapi.glovoapp.com/v2/laas/quotes"

# Import token service from step 1
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'step_1_authentication'))
from token_service import get_bearer_token

# Get token from authentication module
TOKEN = get_bearer_token()

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

# --- 1) If your Excel→JSON produced a dict of sheets, pick the sheet with orders.
# Example shape we expect for each row (adjust to your column names):
# {
#   "pickup_address_id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
#   "pickup_time_utc": "2024-07-24T14:15:22Z",
#   "dest_raw_address": "Carrer de Casp, 111, L'Eixample, 08013 Barcelona",
#   "dest_lat": 41.39637,
#   "dest_lng": 2.17939,
#   "dest_details": "Floor 6 Door 3"
# }

def row_to_payload(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "pickupDetails": {
            "addressBook": {
                "id": row["pickupAddressBookId"],
            },
            "pickupTime": row["pickupTimeUtc"],  # must be ISO8601 UTC with 'Z'
        },
        "deliveryAddress": {
            "rawAddress": row["deliveryRawAddress"],
            "coordinates": {
                "latitude": float(row["deliveryLatitude"]),
                "longitude": float(row["deliveryLongitude"]),
            },
            "details": row.get("deliveryDetails", ""),
        },
    }

def validate_row(row: Dict[str, Any]) -> Optional[str]:
    """Return None if ok, else an error message describing what's missing/wrong."""
    required = ["pickupAddressBookId", "pickupTimeUtc", "deliveryRawAddress", "deliveryLatitude", "deliveryLongitude"]
    missing = [k for k in required if k not in row or row[k] in (None, "")]
    if missing:
        return f"Missing fields: {', '.join(missing)}"
    # quick type checks
    try:
        float(row["deliveryLatitude"]); float(row["deliveryLongitude"])
    except Exception:
        return "deliveryLatitude/deliveryLongitude must be numeric"
    if not isinstance(row["pickupTimeUtc"], str) or not row["pickupTimeUtc"].endswith("Z"):
        return "pickupTimeUtc must be ISO8601 UTC string ending with 'Z'"
    return None

def send_quote(payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """POST one payload. Returns (ok, response_json_or_error)."""
    try:
        r = requests.post(URL, headers=HEADERS, json=payload, timeout=30)
        if r.status_code >= 200 and r.status_code < 300:
            return True, r.json()
        # try to parse error body
        try:
            return False, {"status": r.status_code, "error": r.json()}
        except Exception:
            return False, {"status": r.status_code, "error": r.text}
    except requests.RequestException as e:
        return False, {"error": str(e)}

def iter_orders_from_memory(workbook: Dict[str, List[Dict[str, Any]]],
                            sheet_name: str) -> Iterable[Dict[str, Any]]:
    """Yield rows from a given sheet inside the workbook dict."""
    for row in workbook.get(sheet_name, []):
        yield row

def iter_orders_from_file(path: str, sheet_name: Optional[str] = None) -> Iterable[Dict[str, Any]]:
    """
    Load orders from a JSON file:
      - If file is a list: it's already the rows
      - If file is a dict of sheets: pass sheet_name to pick the right sheet
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        for row in data:
            yield row
    elif isinstance(data, dict):
        if not sheet_name:
            # pick first sheet if not specified
            sheet_name = next(iter(data.keys()))
        for row in data.get(sheet_name, []):
            yield row
    else:
        raise ValueError("Unsupported JSON structure in file.")

def process_orders(rows: Iterable[Dict[str, Any]],
                   rate_limit_per_sec: float = 5.0) -> Dict[str, Any]:
    """
    Send one request per order with simple rate limiting.
    Returns a summary with successes and failures.
    """
    delay = 1.0 / max(rate_limit_per_sec, 0.001)
    successes = []
    failures = []

    for i, row in enumerate(rows, start=1):
        err = validate_row(row)
        if err:
            failures.append({"index": i, "row": row, "reason": err})
            continue

        payload = row_to_payload(row)
        ok, resp = send_quote(payload)
        if ok:
            successes.append({"index": i, "row": row, "response": resp})
        else:
            failures.append({"index": i, "row": row, "reason": resp})

        time.sleep(delay)  # simple rate limiting

    return {
        "total": len(successes) + len(failures),
        "successes": successes,
        "failures": failures,
    }

if __name__ == "__main__":
    # === Option A: Load directly from Google Sheets ===
    from sheet_to_json import load_workbook_to_dict
    
    # Your actual Google Sheets URL
    google_sheets_url = "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?usp=sharing&ouid=100766369247091180171&rtpof=true&sd=true"
    
    print("Loading data from Google Sheets...")
    workbook = load_workbook_to_dict(google_sheets_url)
    
    # Find the sheet with order data (it might be named differently)
    sheet_names = list(workbook.keys())
    print(f"Available sheets: {sheet_names}")
    
    # Use the first sheet that contains data
    sheet_name = sheet_names[0] if sheet_names else "Sheet1"
    print(f"Using sheet: {sheet_name}")
    
    rows = iter_orders_from_memory(workbook, sheet_name=sheet_name)
    summary = process_orders(rows, rate_limit_per_sec=3.0)  # Slower rate for production

    print("\n=== Summary ===")
    print(f"Total: {summary['total']}")
    print(f"Successes: {len(summary['successes'])}")
    print(f"Failures: {len(summary['failures'])}")

    # Save results for Step 3
    results_file = "quote_results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\nQuote results saved to: {results_file}")
    print("You can now run Step 3 to create orders with these quote IDs.")

    if summary["failures"]:
        # show a couple of failures for debugging
        print("\nSample failures:")
        for f in summary["failures"][:3]:
            print(json.dumps(f, indent=2))
