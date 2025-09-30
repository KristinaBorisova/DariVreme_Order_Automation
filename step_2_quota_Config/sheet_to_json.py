#!/usr/bin/env python3
"""
sheet_to_json.py
Convert a public Google Sheet (URL) or a local .xlsx to JSON.

- import usage:
    from sheet_to_json import convert_sheet_to_json, load_workbook_to_dict
    convert_sheet_to_json(url_or_path, outdir="json_export")
    data = load_workbook_to_dict(url_or_path)  # in-memory dict

- CLI usage:
    python sheet_to_json.py "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit" -o json_export
"""
import argparse
import io
import json
import os
import re
import sys
from typing import Dict, List, Any

import pandas as pd
import requests

GOOGLE_EXPORT_TPL = "https://docs.google.com/spreadsheets/d/{sid}/export?format=xlsx"

def is_google_sheet(url_or_path: str) -> bool:
    return url_or_path.startswith("http") and "docs.google.com/spreadsheets/d/" in url_or_path

def extract_spreadsheet_id(url: str) -> str:
    m = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
    if not m:
        raise ValueError("Could not extract spreadsheet ID from the provided URL.")
    return m.group(1)

def fetch_xlsx_bytes_from_gsheets(url: str) -> bytes:
    sid = extract_spreadsheet_id(url)
    export_url = GOOGLE_EXPORT_TPL.format(sid=sid)
    r = requests.get(export_url, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(
            f"Failed to download spreadsheet (HTTP {r.status_code}). "
            "Make sure the sheet is shared as 'Anyone with the link'."
        )
    return r.content

def normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    out = {}
    for k, v in record.items():
        if pd.isna(v):
            out[k] = None
        elif isinstance(v, pd.Timestamp):
            out[k] = v.isoformat()
        elif isinstance(v, pd.Timedelta):
            out[k] = str(v)
        else:
            if hasattr(v, "item"):
                try:
                    out[k] = v.item()
                    continue
                except Exception:
                    pass
            out[k] = v
    return out

def dataframe_to_records(df: "pd.DataFrame") -> List[Dict[str, Any]]:
    df = df.dropna(how="all").dropna(axis=1, how="all").reset_index(drop=True)
    return [normalize_record(rec) for rec in df.to_dict(orient="records")]

def sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    return name.strip() or "Sheet"

def export_workbook_to_json(xlsx_bytes: bytes, outdir: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Writes one JSON per sheet + workbook.json. Also returns the combined dict.
    """
    os.makedirs(outdir, exist_ok=True)
    xls = pd.ExcelFile(io.BytesIO(xlsx_bytes))
    combined: Dict[str, List[Dict[str, Any]]] = {}

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name, dtype=object)
        records = dataframe_to_records(df)
        combined[sheet_name] = records

        safe = sanitize_filename(sheet_name)
        with open(os.path.join(outdir, f"{safe}.json"), "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

    with open(os.path.join(outdir, "workbook.json"), "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
    return combined

def convert_sheet_to_json(input_source: str, outdir: str = "json_export") -> Dict[str, List[Dict[str, Any]]]:
    """
    Convert a Google Sheet (URL) or local XLSX file to JSON files.
    Returns the combined dict as well.
    """
    if is_google_sheet(input_source):
        xlsx_bytes = fetch_xlsx_bytes_from_gsheets(input_source)
    else:
        with open(input_source, "rb") as f:
            xlsx_bytes = f.read()
    return export_workbook_to_json(xlsx_bytes, outdir)

def load_workbook_to_dict(input_source: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Load a Google Sheet (URL) or local XLSX into memory as a dict:
      { "Sheet1": [ {col: val, ...}, ... ], ... }
    No files are written.
    """
    if is_google_sheet(input_source):
        xlsx_bytes = fetch_xlsx_bytes_from_gsheets(input_source)
    else:
        with open(input_source, "rb") as f:
            xlsx_bytes = f.read()

    xls = pd.ExcelFile(io.BytesIO(xlsx_bytes))
    combined: Dict[str, List[Dict[str, Any]]] = {}
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name, dtype=object)
        combined[sheet_name] = dataframe_to_records(df)
    return combined

def main():
    ap = argparse.ArgumentParser(description="Export Google Sheet or XLSX workbook to JSON per sheet.")
    ap.add_argument("input", help="Public Google Sheets link OR path to local .xlsx file")
    ap.add_argument("-o", "--outdir", default="json_export", help="Output directory (default: json_export)")
    args = ap.parse_args()

    convert_sheet_to_json(args.input, args.outdir)
    print(f"Done. JSON written to: {args.outdir}")

if __name__ == "__main__":
    main()
