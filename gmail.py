#!/usr/bin/env python3
"""
gmail.py — accesso a Gmail via OAuth 2.0 device flow (Google API).

NON usa password. NON usa service account. L'autenticazione avviene nel
browser dell'utente; questo script riceve solo un token di refresh.

Setup (una volta sola):
  1. console.cloud.google.com -> crea/seleziona un progetto
  2. abilita "Gmail API"
  3. OAuth consent screen -> External -> aggiungi il tuo indirizzo come Test user
  4. Credentials -> OAuth client ID -> Desktop app
  5. scarica il JSON e salvalo come  ./credentials.json
  6. python3 gmail.py auth
  7. incolla qui il codice che ti mostra il terminale

Poi:  python3 gmail.py list
      python3 gmail.py search "from:newsletter newer_than:30d"
      python3 gmail.py get <messageId>
      python3 gmail.py export "newer_than:90d"   -> out/ come .mbox

Dipendenze: nessuna (solo stdlib).
"""

import json
import os
import sys
import time
import base64
import email
import urllib.request
import urllib.parse
import urllib.error
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
CREDS = HERE / "credentials.json"
TOKEN = HERE / "token.json"
OUT = HERE / "out"

SCOPES = "https://www.googleapis.com/auth/gmail.readonly"
AUTH_URI = "https://oauth2.googleapis.com/device/code"
TOKEN_URI = "https://oauth2.googleapis.com/token"
API = "https://gmail.googleapis.com/gmail/v1/users/me"


# ---------------------------------------------------------------- plumbing

def die(msg, code=1):
    print(f"errore: {msg}", file=sys.stderr)
    sys.exit(code)


def post_form(url, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        die(f"HTTP {e.code}: {e.read().decode()[:300]}")


def get_json(url, token):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 401:
            die("token non valido: riesegui  python3 gmail.py auth")
        die(f"HTTP {e.code}: {e.read().decode()[:300]}")


# ---------------------------------------------------------------- auth

def load_creds():
    if not CREDS.exists():
        die(f"manca {CREDS.name} — scarica l'OAuth client ID (Desktop app) "
            f"da Google Cloud Console e salvalo in questa cartella")
    c = json.loads(CREDS.read_text())
    d = c.get("installed") or c.get("web") or c.get("desktop")
    if not d:
        die("credentials.json ha una forma inattesa")
    return d["client_id"], d.get("client_secret", "")


def refresh(d):
    """Rinnova il token. Ritorna l'access token fresco."""
    if not TOKEN.exists():
        die("non autenticato: esegui  python3 gmail.py auth")
    t = json.loads(TOKEN.read_text())
    if t.get("refresh_token"):
        r = post_form(TOKEN_URI, {
            "client_id": d[0], "client_secret": d[1],
            "refresh_token": t["refresh_token"], "grant_type": "refresh_token",
        })
        return r["access_token"]
    if t.get("access_token") and t.get("expires_at", 0) > time.time() + 60:
        return t["access_token"]
    die("refresh token assente: riesegui  python3 gmail.py auth")


def cmd_auth(_):
    cid, secret = load_creds()
    print("richiedo il codice al server Google...\n")
    r = post_form(AUTH_URI, {"client_id": cid, "scope": SCOPES})
    print("=" * 66)
    print(r["verification_url"])
    print("codice: " + r["user_code"])
    print("=" * 66)
    print("\nAprilo nel browser e incolla qui il codice approvato.\n")

    got = input("codice> ").strip()
    resp = post_form(TOKEN_URI, {
        "client_id": cid, "client_secret": secret,
        "device_code": r["device_code"], "grant_type":
        "urn:ietf:params:oauth:grant-type:device_code", "code": got,
    })
    TOKEN.write_text(json.dumps({
        "access_token": resp["access_token"],
        "refresh_token": resp.get("refresh_token"),
        "expires_at": time.time() + resp.get("expires_in", 3600),
        "scope": resp.get("scope"),
    }, indent=2))
    TOKEN.chmod(0o600)
    print(f"\nok. token salvato in {TOKEN.name} (solo lettura: {SCOPES})")


# ---------------------------------------------------------------- commands

def hdr(m, name, default=""):
    for h in m.get("payload", {}).get("headers", []):
        if h["name"].lower() == name:
            return h["value"]
    return default


def summarize(m):
    return {
        "id": m["id"],
        "date": hdr(m, "date"),
        "from": hdr(m, "from"),
        "subject": hdr(m, "subject"),
        "unread": "UNREAD" in m.get("labelIds", []),
    }


def cmd_list(argv):
    if not argv:
        die("uso: gmail.py list [n=20]")
    n = int(argv[0]) if argv[0].isdigit() else 20
    d = load_creds()
    t = refresh(d)
    data = get_json(f"{API}/messages?maxResults={n}", t)
    msgs = data.get("messages", [])
    for mid in [m["id"] for m in msgs]:
        m = get_json(f"{API}/messages/{mid}?format=metadata", t)
        s = summarize(m)
        flag = "U" if s["unread"] else " "
        print(f"[{flag}] {s['date'][:31]:<31} | {s['from'][:34]:<34} | {s['subject'][:60]}")
    print(f"\n{len(msgs)} messaggi.  dettaglio: gmail.py get <id>")


def cmd_search(argv):
    if not argv:
        die("es. gmail.py search \"from:newsletter newer_than:30d\"")
    q = " ".join(argv)
    d = load_creds()
    t = refresh(d)
    url = f"{API}/messages?" + urllib.parse.urlencode({"q": q, "maxResults": 50})
    msgs = get_json(url, t).get("messages", [])
    print(f"query: {q}\n")
    for m in msgs:
        d2 = get_json(f"{API}/messages/{m['id']}?format=metadata", t)
        s = summarize(d2)
        print(f"{s['id']}  {s['date'][:31]:<31} | {s['from'][:30]:<30} | {s['subject'][:55]}")
    print(f"\n{len(msgs)} risultati.")


def walk(part, acc):
    if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
        acc.append(base64.urlsafe_b64decode(part["body"]["data"]).decode(
            "utf-8", "replace"))
    for p in part.get("parts", []) or []:
        walk(p, acc)


def cmd_get(argv):
    if not argv:
        die("uso: gmail.py get <messageId>")
    d = load_creds()
    t = refresh(d)
    m = get_json(f"{API}/messages/{argv[0]}?format=full", t)
    body = []
    walk(m["payload"], body)
    print(f"From:    {hdr(m,'from')}\nTo:      {hdr(m,'to')}\n"
          f"Date:    {hdr(m,'date')}\nSubject: {hdr(m,'subject')}\n")
    print("-" * 66)
    print("\n".join(body) or "(nessun corpo testuale)")


def cmd_export(argv):
    q = " ".join(argv) if argv else "newer_than:90d"
    d = load_creds()
    t = refresh(d)
    url = f"{API}/messages?" + urllib.parse.urlencode({"q": q, "maxResults": 200})
    ids = [m["id"] for m in get_json(url, t).get("messages", [])]
    OUT.mkdir(exist_ok=True)
    dest = OUT / "export.mbox"
    with dest.open("w") as fh:
        for mid in ids:
            raw = get_json(f"{API}/messages/{mid}?format=raw", t)
            data = base64.urlsafe_b64decode(raw["raw"] + "===")
            msg = email.message_from_bytes(data)
            fh.write(msg.as_string() + "\n\n")
    print(f"{len(ids)} messaggi -> {dest}  (leggibile con ogni client email)")


COMMANDS = {
    "auth": cmd_auth, "list": cmd_list, "search": cmd_search,
    "get": cmd_get, "export": cmd_export,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        sys.exit(0 if len(sys.argv) < 2 else 1)
    COMMANDS[sys.argv[1]](sys.argv[2:])
