import json, os, sqlite3, urllib.request
from datetime import datetime

BASE = os.environ.get("ANIME_BASE", os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE, "data", "recommender.db")
ANILIST_URL = "https://graphql.anilist.co"

def fetch_page(page):
    query = """
    query ($page: Int, $perPage: Int) {
      Page(page: $page, perPage: $perPage) {
        media(type: ANIME, format: MOVIE, sort: SCORE_DESC, status: FINISHED) {
          title { romaji english }
          startDate { year }
          meanScore
          popularity
          genres
          studios { nodes { name } }
          source(version: 2)
        }
      }
    }
    """
    data = json.dumps({"query": query, "variables": {"page": page, "perPage": 50}}).encode()
    req = urllib.request.Request(ANILIST_URL, data=data, headers={
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Hermes-OWL/2.0)"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except Exception as e:
        print("HATA:", e)
        return None

# 10 sayfa = 500 film
all_films = []
for page in range(1, 11):
    result = fetch_page(page)
    if result and "data" in result:
        items = result["data"]["Page"]["media"]
        for m in items:
            title = m["title"]["romaji"] or m["title"]["english"] or "Unknown"
            year = m.get("startDate", {}).get("year") or 2000
            score = (m.get("meanScore") or 70) / 10
            genres = m.get("genres", [])
            studio = m["studios"]["nodes"][0]["name"] if m.get("studios", {}).get("nodes") else "Unknown"
            src_map = {"ORIGINAL": "Original", "MANGA": "Manga", "LIGHT_NOVEL": "Light Novel", "NOVEL": "Novel", "VISUAL_NOVEL": "Visual Novel", "WEB_NOVEL": "Web Novel", "GAME": "Game"}
            src = src_map.get(m.get("source", ""), "Other")
            all_films.append({"title": title, "year": year, "score": score, "genres": genres, "studio": studio, "source": src, "popularity": m.get("popularity", 0)})
        print("Sayfa %d: %d film" % (page, len(items)))
    else:
        print("Sayfa %d: HATA" % page)

print("\nToplam cekilen: %d film" % len(all_films))

# DB olustur/guncelle
db = sqlite3.connect(DB_PATH)
db.executescript("""
    CREATE TABLE IF NOT EXISTS films(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, title_lower TEXT UNIQUE,
        year INTEGER, director TEXT DEFAULT '',
        studio TEXT DEFAULT 'Unknown',
        mal_score REAL DEFAULT 0, imdb_score REAL DEFAULT 0, owl_score REAL DEFAULT 0,
        source TEXT DEFAULT 'Unknown', genres TEXT DEFAULT '',
        popularity INTEGER DEFAULT 0, is_watched INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_fo ON films(owl_score DESC);
    CREATE INDEX IF NOT EXISTS idx_fw ON films(is_watched);
    CREATE INDEX IF NOT EXISTS idx_ft ON films(title_lower);
""")

TASTE = {"Philosophical": 10, "Psychological": 9, "Action": 9, "Drama": 8, "Fantasy": 8, "Comedy": 8, "Sci-Fi": 7, "Slice of Life": 7, "Thriller": 7, "Romance": 5, "Mecha": 6, "Horror": 6, "Mystery": 7, "Suspense": 7, "Ecchi": 4}

added = updated = 0
for f in all_films:
    tl = f["title"].lower()
    gj = json.dumps(f["genres"])
    base = f["score"]
    gb = sum(TASTE.get(g, 5) for g in f["genres"]) / max(len(f["genres"]), 1) * 0.05
    yb = 0.15 if f["year"] >= 2020 else (0.08 if f["year"] >= 2010 else 0)
    ow = min(round(base + gb + yb, 1), 10.0)
    try:
        db.execute("INSERT INTO films(title,title_lower,year,studio,mal_score,owl_score,source,genres,popularity) VALUES(?,?,?,?,?,?,?,?,?)",
                   (f["title"], tl, f["year"], f["studio"], f["score"], ow, f["source"], gj, f["popularity"]))
        added += 1
    except sqlite3.IntegrityError:
        db.execute("UPDATE films SET mal_score=?,owl_score=?,genres=?,popularity=? WHERE title_lower=?", (f["score"], ow, gj, f["popularity"], tl))
        updated += 1

db.commit()
total = db.execute("SELECT COUNT(*) FROM films").fetchone()[0]
print("\n=== SONUC ===")
print("Eklenen: %d" % added)
print("Guncellenen: %d" % updated)
print("Toplam DB: %d" % total)

# Ilk 10 oneri goster
print("\n=== ILK 10 ONERI ===")
for row in db.execute("SELECT title,year,owl_score,source FROM films WHERE is_watched=0 ORDER BY owl_score DESC LIMIT 10").fetchall():
    print("  [%.1f] %s (%d) - %s" % (row[2], row[0], row[1], row[3]))
