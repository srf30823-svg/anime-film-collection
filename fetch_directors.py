#!/usr/bin/env python3
"""Jikan API ile bos director bilgilerini doldur."""
import urllib.request, json, time, sqlite3, os, urllib.parse, sys

BASE = os.environ.get("ANIME_BASE", os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE, "data", "recommender.db")
JIKAN_BASE = "https://api.jikan.moe/v4"

def jikan_search_one(title):
    url = f"{JIKAN_BASE}/anime?type=movie&limit=1&q={urllib.parse.quote(title)}"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read()).get("data", [])
                return data[0] if data else None
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = int(e.headers.get("Retry-After", 5))
                print(f"  RL {wait}s...", flush=True)
                time.sleep(wait + 1)
                continue
            return None
        except:
            return None
    return None

def jikan_get_staff(mal_id):
    url = f"{JIKAN_BASE}/anime/{mal_id}/staff"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            staff = json.loads(r.read()).get("data", [])
            dirs = [s["person"]["name"] for s in staff
                    if "Director" in s.get("positions", []) and s.get("person", {}).get("name")]
            return ", ".join(dirs) if dirs else ""
    except:
        return ""

db = sqlite3.connect(DB_PATH)
# row_factory olmadan calis — tuple olarak eris
rows = db.execute(
    "SELECT id, title FROM films WHERE director = '' OR director IS NULL ORDER BY owl_score DESC"
).fetchall()

total = len(rows)
print(f"Bos director: {total} film", flush=True)

filled = failed = 0
for i, row in enumerate(rows, 1):
    film_id = row[0]
    film_title = row[1]

    result = jikan_search_one(film_title)
    if not result:
        failed += 1
        time.sleep(0.8)
        continue

    mal_id = result.get("mal_id")
    if not mal_id:
        failed += 1
        time.sleep(0.8)
        continue

    time.sleep(0.4)
    directors = jikan_get_staff(mal_id)
    if directors:
        db.execute("UPDATE films SET director = ? WHERE id = ?", (directors, film_id))
        filled += 1
        if filled <= 15 or filled % 25 == 0:
            print(f"  + {film_title[:45]} → {directors[:60]}", flush=True)
    else:
        failed += 1

    time.sleep(0.8)

    if i % 50 == 0:
        db.commit()
        hd = db.execute("SELECT COUNT(*) FROM films WHERE director!=''").fetchone()[0]
        pct = hd * 100 // 602
        print(f"  [{i}/{total}] Director: {hd}/602 ({pct}%), +{filled}", flush=True)
        sys.stdout.flush()

db.commit()
hd = db.execute("SELECT COUNT(*) FROM films WHERE director!=''").fetchone()[0]
pct = hd * 100 // 602
print(f"\nTAMAM: {filled} yeni director eklendi", flush=True)
print(f"Toplam: {hd}/602 ({pct}%)", flush=True)
db.close()
