#!/usr/bin/env python3
"""Verifica le email di club-privati-email.csv aprendo la fonte (via curl)."""
import csv, re, subprocess, pathlib, sys, urllib.parse
from concurrent.futures import ThreadPoolExecutor

CSV = pathlib.Path(__file__).with_name("club-privati-email.csv")
COLS = ["nazione", "club", "email", "verifica", "fonte"]
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36")
_cache = {}


def fetch(url):
    if url in _cache:
        return _cache[url]
    try:
        r = subprocess.run(["curl", "-sL", "-A", UA, "--max-time", "30",
                            "--compressed", url], capture_output=True, timeout=45)
        t = r.stdout.decode("utf-8", "replace")
        t = t.replace("&#64;", "@").replace("&#046;", ".")
        _cache[url] = t if t.strip() else None
    except Exception:
        _cache[url] = None
    return _cache[url]


def decode_cfemail(hexstr):
    try:
        r = int(hexstr[:2], 16)
        return "".join(chr(int(hexstr[i:i + 2], 16) ^ r)
                       for i in range(2, len(hexstr), 2))
    except Exception:
        return ""


def verify(row):
    email, src = row["email"].strip(), row["fonte"].strip()
    text = fetch(src)
    if text is None:
        return row, "FONTE IRRAGGIUNGIBILE"
    if email.lower() in text.lower():
        return row, "VERIFICATA"
    for enc in re.findall(r'data-cfemail="([0-9a-fA-F]+)"', text):
        if decode_cfemail(enc).lower() == email.lower():
            return row, "VERIFICATA (cfemail)"
    return row, "NON CONFERMATA"


def main():
    rows = list(csv.DictReader(CSV.open()))
    todo = [r for r in rows if "--all" in sys.argv or not r["verifica"].startswith("VERIFICATA")]
    with ThreadPoolExecutor(max_workers=6) as ex:
        results = list(ex.map(verify, todo))
    by = {(r["email"], r["fonte"]): s for r, s in results}
    for r in rows:
        if (r["email"], r["fonte"]) in by:
            r["verifica"] = by[(r["email"], r["fonte"])]
    for r, s in results:
        flag = {"VERIFICATA": "OK ", "NON CONFERMATA": "?? ",
                "FONTE IRRAGGIUNGIBILE": "XX "}.get(s, "   ")
        print(f"{flag} {r['nazione'][:14]:<14} {r['email'][:44]:<44} {s}")
    with CSV.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); w.writerows(rows)
    from collections import Counter
    print("\n--- riepilogo ---")
    for k, v in Counter(r["verifica"] for r in rows).most_common():
        print(f"{v:>4}  {k}")
    print(f"club: {len(rows)} | nazioni: {len(set(r['nazione'] for r in rows))}")


if __name__ == "__main__":
    main()
