"""Tiny Storyblok Management API helper for the Meilleurtaux demo build scripts.

Token: STORYBLOK_MANAGEMENT_TOKEN in the environment. Never commit it.
"""
import json
import os
import time
import urllib.error
import urllib.request

SPACE = 296195186860676
BASE = f"https://mapi.storyblok.com/v1/spaces/{SPACE}"
TOKEN = os.environ["STORYBLOK_MANAGEMENT_TOKEN"]


def api(method, path, body=None, retries=6):
    url = path if path.startswith("http") else BASE + path
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, method=method,
                                     headers={"Authorization": TOKEN, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as r:
                time.sleep(0.25)
                raw = r.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise RuntimeError(f"{method} {path} -> {e.code}: {e.read().decode()[:600]}")


def all_pages(path, key):
    out, page = [], 1
    while True:
        sep = "&" if "?" in path else "?"
        d = api("GET", f"{path}{sep}per_page=100&page={page}")
        items = d.get(key, [])
        out += items
        if len(items) < 100:
            return out
        page += 1
