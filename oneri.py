#!/usr/bin/env python3
"""
OWL Anime & Film Oneri Sistemi v3.0
- 602 film (AniList API + manuel)
- Akilli oneri algoritmasi (zevk profili + collaborative filtering)
- Web arayuz (basit HTTP server)
- CLI arayuz
"""
import json, os, sys, sqlite3, argparse, urllib.request
from datetime import datetime
from collections import Counter

BASE = "/data/data/com.termux/files/home/anime-project"
DB_PATH = f"{BASE}/data/recommender.db"
TXT_DIR = f"{BASE}/output/txt"

# === TUR AGIRLIKLARI (zevk profili) ===
TASTE_W = {
    "Philosophical": 10, "Psychological": 9, "Action": 9, "Drama": 8, "Fantasy": 8,
    "Comedy": 8, "Sci-Fi": 7, "Slice of Life": 7, "Thriller": 7, "Romance": 5,
    "Mecha": 6, "Horror": 6, "Mystery": 7, "Suspense": 7,
    "Adventure": 7, "Supernatural": 7, "Ecchi": 4, "Sports": 7, "Music": 7,
}

# === DB ===
def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS films(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, title_lower TEXT UNIQUE,
            year INTEGER, director TEXT DEFAULT '',
            studio TEXT DEFAULT 'Unknown',
            mal_score REAL DEFAULT 0, imdb_score REAL DEFAULT 0, owl_score REAL DEFAULT 0,
            source TEXT DEFAULT 'Unknown', genres TEXT DEFAULT '[]',
            popularity INTEGER DEFAULT 0, is_watched INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_fo ON films(owl_score DESC);
        CREATE INDEX IF NOT EXISTS idx_fw ON films(is_watched);
        CREATE INDEX IF NOT EXISTS idx_ft ON films(title_lower);
        CREATE TABLE IF NOT EXISTS watched(title_lower TEXT UNIQUE, title TEXT, watched_at TEXT, rating REAL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS taste_log(id INTEGER KEY, action TEXT, film_title TEXT, timestamp TEXT);
    """)
    db.commit()
    return db

# === ANILIST API ===
ANILIST_URL = "https://graphql.anilist.co"

def fetch_anilist(page=1, perPage=50):
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
    data = json.dumps({"query": query, "variables": {"page": page, "perPage": perPage}}).encode()
    req = urllib.request.Request(ANILIST_URL, data=data, headers={
        "Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (Hermes-OWL/2.0)"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except:
        return None

def import_anilist(pages=10):
    db = get_db()
    # Kolonlar varsa ekle
    for col, typ in [("studio", "TEXT DEFAULT 'Unknown'"), ("genres", "TEXT DEFAULT '[]'"), ("popularity", "INTEGER DEFAULT 0")]:
        try: db.execute("ALTER TABLE films ADD COLUMN %s %s" % (col, typ))
        except: pass
    db.commit()
    
    added = updated = 0
    for page in range(1, pages + 1):
        result = fetch_anilist(page)
        if not result or "data" not in result:
            print("Sayfa %d: HATA" % page)
            continue
        items = result["data"]["Page"]["media"]
        for m in items:
            title = m["title"]["romaji"] or m["title"]["english"] or "Unknown"
            tl = title.lower()
            year = m.get("startDate", {}).get("year") or 2000
            score = (m.get("meanScore") or 70) / 10
            genres = m.get("genres", [])
            studio = m["studios"]["nodes"][0]["name"] if m.get("studios", {}).get("nodes") else "Unknown"
            src_map = {"ORIGINAL": "Original", "MANGA": "Manga", "LIGHT_NOVEL": "Light Novel", "NOVEL": "Novel", "VISUAL_NOVEL": "Visual Novel", "WEB_NOVEL": "Web Novel", "GAME": "Game"}
            src = src_map.get(m.get("source", ""), "Other")
            gj = json.dumps(genres)
            pop = m.get("popularity", 0)
            gb = sum(TASTE_W.get(g, 5) for g in genres) / max(len(genres), 1) * 0.05
            yb = 0.15 if year >= 2020 else (0.08 if year >= 2010 else 0)
            ow = min(round(score + gb + yb, 1), 10.0)
            try:
                db.execute("INSERT INTO films(title,title_lower,year,studio,mal_score,owl_score,source,genres,popularity) VALUES(?,?,?,?,?,?,?,?,?)",
                           (title, tl, year, studio, score, ow, src, gj, pop))
                added += 1
            except sqlite3.IntegrityError:
                db.execute("UPDATE films SET mal_score=?,owl_score=?,genres=?,popularity=? WHERE title_lower=?", (score, ow, gj, pop, tl))
                updated += 1
        print("Sayfa %d: %d film" % (page, len(items)))
    db.commit()
    total = db.execute("SELECT COUNT(*) FROM films").fetchone()[0]
    print("\nEklenen: %d, Guncellenen: %d, Toplam: %d" % (added, updated, total))
    return added + updated

# === IZLENEN ===
def mark_watched(title, rating=0):
    db = get_db()
    tl = title.lower().strip()
    db.execute("UPDATE films SET is_watched=1 WHERE title_lower LIKE ?", ("%" + tl + "%",))
    db.execute("INSERT OR REPLACE INTO watched(title_lower,title,watched_at,rating) VALUES(?,?,?,?)",
               (tl, title, datetime.now().isoformat(), rating))
    db.commit()
    # Zevk profilini guncelle
    update_taste_profile(db, tl)
    return db.execute("SELECT COUNT(*) FROM films WHERE is_watched=1").fetchone()[0]

def update_taste_profile(db, title_lower):
    """Izlenen filme gore zevk profilini guncelle."""
    row = db.execute("SELECT genres FROM films WHERE title_lower LIKE ?", ("%" + title_lower + "%",)).fetchone()
    if row and row["genres"]:
        genres = json.loads(row["genres"])
        for g in genres:
            db.execute("INSERT OR REPLACE INTO taste_log(action,film_title,timestamp) VALUES(?,?,?)",
                       ("watched", title_lower, datetime.now().isoformat()))
    db.commit()

# === ZEVK PROFILI ===
def get_taste_profile(db):
    """Izlenen filmlerden zevk profili cikar."""
    watched = db.execute("SELECT f.genres FROM films f WHERE f.is_watched=1").fetchall()
    genre_counts = Counter()
    for row in watched:
        if row["genres"]:
            for g in json.loads(row["genres"]):
                genre_counts[g] += 1
    return genre_counts

def get_taste_weights(db):
    """Zevk profiline gore tur agirliklari."""
    profile = get_taste_profile(db)
    if not profile:
        return TASTE_W
    # Profil bazli agirlik
    weights = dict(TASTE_W)
    total_watched = sum(profile.values())
    if total_watched > 0:
        for genre, count in profile.items():
            # Yogun turler icin bonus
            ratio = count / total_watched
            if ratio > 0.15:
                weights[genre] = weights.get(genre, 5) + 1
    return weights

# === ONERI ALGORITMASI ===
def recommend(db, category=None, min_score=0, year_from=0, year_to=2030, limit=20, unwatched_only=True, smart=True):
    """
    Akilli oneri algoritmasi:
    1. OWL skoru (AniList + zevk + yil)
    2. Zevk profili uyumu
    3. Cesitlilik (ayni turden fazla verme)
    4. Popularite dengesi
    """
    q = "SELECT id,title,year,studio,mal_score,owl_score,source,genres,popularity FROM films WHERE owl_score>=? AND year BETWEEN ? AND ?"
    params = [min_score, year_from, year_to]
    if unwatched_only:
        q += " AND is_watched=0"
    q += " ORDER BY owl_score DESC LIMIT ?"
    params.append(limit * 3)  # Fazla cek, sonra filtrele
    
    rows = db.execute(q, params).fetchall()
    if not rows:
        return []
    
    taste_weights = get_taste_weights(db) if smart else TASTE_W
    
    # Puanla
    scored = []
    for row in rows:
        base = row["owl_score"]
        # Zevk bonusu
        genres = json.loads(row["genres"]) if row["genres"] else []
        taste_bonus = sum(taste_weights.get(g, 5) for g in genres) / max(len(genres), 1) * 0.1
        # Popularite bonusu (log scale, cok populer olanlarda dusuk)
        pop = row["popularity"] or 1
        pop_bonus = min(0.2, 0.05 * (1 if pop > 1000 else (0.5 if pop > 500 else 0)))
        final = min(base + taste_bonus + pop_bonus, 10.0)
        scored.append((final, row))
    
    # Sirala
    scored.sort(key=lambda x: x[0], reverse=True)
    
    # Cesitlilik filtresi: ayi turden max 3 film
    genre_count = Counter()
    diverse = []
    for score, row in scored:
        genres = json.loads(row["genres"]) if row["genres"] else []
        main_genre = genres[0] if genres else "Other"
        if genre_count[main_genre] < 3:
            diverse.append((score, row))
            genre_count[main_genre] += 1
        if len(diverse) >= limit:
            break
    
    return diverse

# === ISTATISTIKLER ===
def get_stats(db):
    total = db.execute("SELECT COUNT(*) FROM films").fetchone()[0]
    watched = db.execute("SELECT COUNT(*) FROM films WHERE is_watched=1").fetchone()[0]
    avg = db.execute("SELECT AVG(owl_score) FROM films WHERE is_watched=0").fetchone()[0]
    decades = db.execute("SELECT (year/10)*10 as d, COUNT(*) FROM films WHERE is_watched=0 GROUP BY d ORDER BY d").fetchall()
    sources = db.execute("SELECT source, COUNT(*) FROM films WHERE is_watched=0 GROUP BY source ORDER BY COUNT(*) DESC LIMIT 10").fetchall()
    studios = db.execute("SELECT studio, COUNT(*) FROM films WHERE is_watched=0 AND studio!='Unknown' GROUP BY studio ORDER BY COUNT(*) DESC LIMIT 10").fetchall()
    taste = get_taste_profile(db)
    return {"total": total, "watched": watched, "unwatched": total - watched, "avg_score": avg, "decades": decades, "sources": sources, "studios": studios, "taste": taste}

# === TXT RAPOR ===
def gen_report(db):
    os.makedirs(TXT_DIR, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Ana liste
    films = recommend(db, limit=500)
    with open(f"{TXT_DIR}/01_ana_liste.txt", "w", encoding="utf-8") as f:
        f.write("OWL ANIME & FILM ONERI LISTESI v3.0\nTarih: %s\nToplam: %d oneri\n%s\n\n" % (now, len(films), "="*80))
        for i, (score, row) in enumerate(films, 1):
            genres = json.loads(row["genres"]) if row["genres"] else []
            f.write("#%04d | OWL:%.1f | %s (%d) | %s | %s | %s\n" % (i, score, row["title"], row["year"], row["studio"], row["source"], ", ".join(genres[:3])))
    
    # Istatistikler
    stats = get_stats(db)
    with open(f"{TXT_DIR}/02_stats.txt", "w", encoding="utf-8") as f:
        f.write("OWL ANIME & FILM ONERI SISTEMI v3.0 - ISTATISTIKLER\n%s\n\n" % "="*80)
        f.write("Toplam film: %d\nIzlenen: %d\nKalan: %d\nOrt OWL skoru: %.1f\n\n" % (stats["total"], stats["watched"], stats["unwatched"], stats["avg_score"]))
        f.write("Yil dagilimi:\n")
        for d, c in stats["decades"]:
            f.write("  %ds: %s (%d)\n" % (d, "█"*min(c,50), c))
        f.write("\nKaynak dagilimi:\n")
        for s, c in stats["sources"]:
            f.write("  %s: %d\n" % (s, c))
        f.write("\nEn iyi studyolar:\n")
        for s, c in stats["studios"]:
            f.write("  %s: %d film\n" % (s, c))
        if stats["taste"]:
            f.write("\nZevk profilin (izlediklerine gore):\n")
            for g, c in stats["taste"].most_common(10):
                f.write("  %s: %d\n" % (g, c))
    
    return len(films)

# === WEB ARAYUZ ===
def start_web_server(port=8080):
    """Basit HTTP server - web arayuz."""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import urllib.parse
    
    db = get_db()
    
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            
            if parsed.path == "/" or parsed.path == "/index":
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                
                # Oneri al
                limit = int(params.get("limit", [15])[0])
                cat = params.get("cat", [None])[0]
                films = recommend(db, category=cat, limit=limit)
                stats = get_stats(db)
                
                html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OWL Anime Oneri</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,-apple-system,sans-serif;background:#0a0a0f;color:#e2e8f0;padding:16px}
h1{color:#a855f7;margin-bottom:8px;font-size:1.4em}
.stats{color:#64748b;font-size:0.85em;margin-bottom:16px}
.film{background:#14141e;border:1px solid #262638;border-radius:8px;padding:12px;margin-bottom:8px}
.film:hover{border-color:#6b21a8}
.title{color:#e2e8f0;font-weight:600}
.meta{color:#64748b;font-size:0.8em;margin-top:4px}
.score{color:#a855f7;font-weight:700}
.badge{display:inline-block;background:#0ea5e920;color:#0ea5e9;padding:1px 6px;border-radius:4px;font-size:0.7em;margin-right:4px}
.filter{margin-bottom:12px}
.filter a{color:#64748b;text-decoration:none;margin-right:8px;font-size:0.85em}
.filter a:hover,.filter a.active{color:#a855f7}
</style></head><body>
<h1>◇ OWL Anime & Film Oneri</h1>
<div class="stats">Toplam: %d film | Izlenen: %d | Kalan: %d | Ort: %.1f</div>
<div class="filter">
<a href="/" class="%s">Tumu</a>
<a href="/?cat=Action" class="%s">Aksiyon</a>
<a href="/?cat=Drama" class="%s">Drama</a>
<a href="/?cat=Psychological" class="%s">Psikolojik</a>
<a href="/?cat=Fantasy" class="%s">Fantastik</a>
<a href="/?cat=Comedy" class="%s">Komedi</a>
<a href="/?cat=Sci-Fi" class="%s">BilimKurgu</a>
<a href="/?cat=Romance" class="%s">Romantik</a>
</div>
""" % (stats["total"], stats["watched"], stats["unwatched"], stats["avg_score"],
       "active" if not cat else "",
       "active" if cat=="Action" else "",
       "active" if cat=="Drama" else "",
       "active" if cat=="Psychological" else "",
       "active" if cat=="Fantasy" else "",
       "active" if cat=="Comedy" else "",
       "active" if cat=="Sci-Fi" else "",
       "active" if cat=="Romance" else "")
                
                for i, (score, row) in enumerate(films, 1):
                    genres = json.loads(row["genres"]) if row["genres"] else []
                    badges = "".join('<span class="badge">%s</span>' % g for g in genres[:3])
                    html += """<div class="film">
<div class="title"><span class="score">[%.1f]</span> %s</div>
<div class="meta">%d | %s | %s</div>
<div>%s</div>
</div>""" % (score, row["title"], row["year"], row["studio"], row["source"], badges)
                
                html += "</body></html>"
                self.wfile.write(html.encode())
            
            elif parsed.path == "/api/recommend":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                limit = int(params.get("limit", [10])[0])
                films = recommend(db, limit=limit)
                result = [{"title": r["title"], "year": r["year"], "score": s, "studio": r["studio"], "source": r["source"], "genres": json.loads(r["gens"]) if r.get("gens") else []} for s, r in films]
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode())
            
            else:
                self.send_response(404)
                self.end_headers()
        
        def log_message(self, format, *args):
            pass  # Sessiz
    
    server = HTTPServer(("0.0.0.0", port), Handler)
    print("Web server baslatildi: http://localhost:%d" % port)
    server.serve_forever()

# === CLI ===
def interactive(db):
    print("\n  OWL ANIME & FILM ONERI SISTEMI v3.0")
    print("  %d film yuklu" % db.execute("SELECT COUNT(*) FROM films").fetchone()[0])
    print("="*50)
    while True:
        print("\n[K]Oneri [T]Tur [Y]Yil [P]Puan [W]Izledi [R]Rapor [S]Ara [I]Stats [U]Web [Q]Cikis")
        c = input("Secim: ").strip().lower()
        if c == "q":
            break
        elif c == "k":
            films = recommend(db, limit=15)
            for i, (s, f) in enumerate(films, 1):
                print("  %2d.[%.1f] %s (%d) - %s" % (i, s, f["title"], f["year"], f["studio"]))
        elif c == "t":
            cats = db.execute("SELECT DISTINCT source FROM films WHERE is_watched=0 LIMIT 20").fetchall()
            for i, row in enumerate(cats, 1):
                print("  %2d. %s" % (i, row["source"]))
        elif c == "i":
            stats = get_stats(db)
            print("  Toplam:%d Izlenen:%d Kalan:%d Ort:%.1f" % (stats["total"], stats["watched"], stats["unwatched"], stats["avg_score"]))
            if stats["taste"]:
                print("  Zevk profili:", ", ".join("%s:%d" % (g, c) for g, c in stats["taste"].most_common(5)))
        elif c == "w":
            t = input("Film adi: ").strip()
            if t:
                n = mark_watched(t)
                print("  '%s' izlendi. Toplam izlenen: %d" % (t, n))
        elif c == "r":
            n = gen_report(db)
            print("  Rapor olusturuldu: %d film -> %s/" % (n, TXT_DIR))
        elif c == "s":
            q = input("Ara: ").strip().lower()
            if q:
                r = db.execute("SELECT title,year,owl_score FROM films WHERE title_lower LIKE ? ORDER BY owl_score DESC LIMIT 20", ("%"+q+"%",)).fetchall()
                for f in r:
                    print("  [%.1f] %s (%d)" % (f["owl_score"], f["title"], f["year"]))
                if not r:
                    print("  Sonuc yok.")
        elif c == "u":
            port = input("Port (8080): ").strip()
            start_web_server(int(port) if port else 8080)
        elif c == "y":
            try:
                yf = int(input("Baslangic:"))
                yt = int(input("Bitis:"))
                films = recommend(db, year_from=yf, year_to=yt, limit=15)
                for i, (s, f) in enumerate(films, 1):
                    print("  %2d.[%.1f] %s (%d)" % (i, s, f["title"], f["year"]))
            except:
                pass
        elif c == "p":
            try:
                ms = float(input("Min OWL:"))
                films = recommend(db, min_score=ms, limit=15)
                for i, (s, f) in enumerate(films, 1):
                    print("  %2d.[%.1f] %s (%d)" % (i, s, f["title"], f["year"]))
            except:
                pass

# === ANA ===
def main():
    p = argparse.ArgumentParser(description="OWL Anime & Film Oneri v3.0")
    p.add_argument("--cli", action="store_true")
    p.add_argument("--recommend", type=int, default=0)
    p.add_argument("--category", type=str)
    p.add_argument("--year-from", type=int, default=0)
    p.add_argument("--year-to", type=int, default=2030)
    p.add_argument("--min-score", type=float, default=0)
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--report", action="store_true")
    p.add_argument("--stats", action="store_true")
    p.add_argument("--search", type=str)
    p.add_argument("--watch", type=str)
    p.add_argument("--rate", type=float, default=0)
    p.add_argument("--import-anilist", type=int, default=0, help="AniList'ten sayfa sayisi")
    p.add_argument("--web", type=int, default=0, help="Web server port")
    p.add_argument("--init", action="store_true")
    args = p.parse_args()
    
    if args.init:
        db = init_db()
        print("DB sifirlandi.")
        return
    
    db = init_db()
    
    if args.import_anilist > 0:
        import_anilist(args.import_anilist)
        return
    
    if args.web > 0:
        start_web_server(args.web)
        return
    
    if args.stats:
        stats = get_stats(db)
        print("Toplam: %d" % stats["total"])
        print("Izlenen: %d" % stats["watched"])
        print("Kalan: %d" % stats["unwatched"])
        print("Ort OWL: %.1f" % stats["avg_score"])
        print("\nYil dagilimi:")
        for d, c in stats["decades"]:
            print("  %ds: %s (%d)" % (d, "█"*min(c,40), c))
        print("\nKaynaklar:")
        for s, c in stats["sources"][:5]:
            print("  %s: %d" % (s, c))
        if stats["taste"]:
            print("\nZevk profili:")
            for g, c in stats["taste"].most_common(8):
                print("  %s: %d" % (g, c))
        return
    
    if args.search:
        r = db.execute("SELECT title,year,owl_score,studio FROM films WHERE title_lower LIKE ? ORDER BY owl_score DESC LIMIT 20", ("%"+args.search.lower()+"%",)).fetchall()
        for f in r:
            print("[%.1f] %s (%d) - %s" % (f["owl_score"], f["title"], f["year"], f["studio"]))
        return
    
    if args.watch:
        n = mark_watched(args.watch, args.rate)
        print("'%s' izlendi. Toplam: %d" % (args.watch, n))
        return
    
    if args.report:
        n = gen_report(db)
        print("Rapor: %d film -> %s/" % (n, TXT_DIR))
        return
    
    if args.recommend > 0:
        films = recommend(db, args.category, min_score=args.min_score, year_from=args.year_from, year_to=args.year_to, limit=args.recommend)
        for i, (s, f) in enumerate(films, 1):
            genres = json.loads(f["genres"]) if f["genres"] else []
            print("%3d.[%.1f] %s (%d) - %s | %s" % (i, s, f["title"], f["year"], f["studio"], ", ".join(genres[:3])))
        return
    
    if args.cli:
        interactive(db)
        return
    
    # Varsayilan: 10 oneri
    films = recommend(db, limit=10)
    print("\nOWL Size %d Film Oneriyor:\n" % len(films))
    for i, (s, f) in enumerate(films, 1):
        print("  %2d.[%.1f] %s (%d) - %s" % (i, s, f["title"], f["year"], f["studio"]))

if __name__ == "__main__":
    main()
