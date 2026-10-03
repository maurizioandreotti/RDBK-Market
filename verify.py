#!/usr/bin/env python3
"""Verifica ogni email del CSV aprendo la sua fonte (via curl) e cercandola.
Schema: nazione,organizzazione,email,verifica,tipo,fonte
Uso:  python3 verify.py            -> verifica solo le righe non ancora VERIFICATA
      python3 verify.py --all      -> riverifica tutto
"""
import csv, re, subprocess, pathlib, sys, urllib.parse
from concurrent.futures import ThreadPoolExecutor

CSV = pathlib.Path(__file__).with_name("club-4x4-email.csv")
COLS = ["nazione", "organizzazione", "email", "verifica", "tipo", "fonte"]
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36")
_cache = {}


def fetch(url):
    if url in _cache:
        return _cache[url]
    try:
        r = subprocess.run(
            ["curl", "-sL", "-A", UA, "--max-time", "30", "--compressed", url],
            capture_output=True, timeout=45)
        text = r.stdout.decode("utf-8", "replace")
        text = text.replace("&#64;", "@").replace("&#046;", ".")
        _cache[url] = text if text.strip() else None
    except Exception:
        _cache[url] = None
    return _cache[url]


def verify(row):
    email = row["email"].strip()
    src = row["fonte"].strip()
    text = fetch(src)
    if text is None:
        return row, "FONTE IRRAGGIUNGIBILE"
    if email.lower() in text.lower():
        return row, "VERIFICATA"
    for m in re.findall(
            r'href="([^"]*(?:contact|kontakt|contacto|iletisim|contatti|kapcsolat)[^"]*)"',
            text, re.I)[:4]:
        sub = m if m.startswith("http") else urllib.parse.urljoin(src, m)
        t2 = fetch(sub)
        if t2 and email.lower() in t2.lower():
            return row, "VERIFICATA"
    return row, "NON CONFERMATA"


def main():
    allflag = "--all" in sys.argv
    rows = list(csv.DictReader(CSV.open()))
    todo = [r for r in rows if allflag or not r["verifica"].startswith("VERIFICATA")]
    with ThreadPoolExecutor(max_workers=6) as ex:
        results = list(ex.map(verify, todo))
    bykey = {(r["email"], r["fonte"]): s for r, s in results}
    for row in rows:
        k = (row["email"], row["fonte"])
        if k in bykey:
            row["verifica"] = bykey[k]
    for r, s in results:
        flag = {"VERIFICATA": "OK ", "NON CONFERMATA": "?? ",
                "FONTE IRRAGGIUNGIBILE": "XX "}.get(s, "   ")
        print(f"{flag} {r['nazione'][:16]:<16} {r['email'][:44]:<44} {r['fonte'][:38]}")
    with CSV.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print("\n--- riepilogo totale ---")
    for k, v in Counter(r["verifica"] for r in rows).most_common():
        print(f"{v:>4}  {k}")
    print(f"righe: {len(rows)} | nazioni: {len(set(r['nazione'] for r in rows))}")


if __name__ == "__main__":
    main()
