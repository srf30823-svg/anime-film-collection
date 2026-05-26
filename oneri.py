#!/usr/bin/env python3
"""
OWL Anime & Film Oneri Sistemi v4.0
- 602 film (AniList API + manuel)
- Content-based collaborative filtering
- Tur/yil/kaynak/format/puan filtresi
- Kullanici puani ve not sistemi
- Modern web arayuzu (responsive, arama, detay sayfasi)
- JSON API (REST-like)
- CLI arayuz

Kullanim:
  python3 oneri.py                          # Varsayilan: 10 oneri
  python3 oneri.py --recommend 20           # 20 oneri
  python3 oneri.py --category Action        # Kategori filtresi
  python3 oneri.py --year-from 2020          # Yil filtresi
  python3 oneri.py --genre Psychological    # Tur filtresi
  python3 oneri.py --studio "Studio Ghibli" # Studio filtresi
  python3 oneri.py --min-score 8.5           # Min OWL puani
  python3 oneri.py --source Manga            # Kaynak filtresi
  python3 oneri.py --watched                 # Izlenmemisleri goster
  python3 oneri.py --search "your name"     # Arama
  python3 oneri.py --watch 1                 # Film izlendi (id)
  python3 oneri.py --rate 1 9.5             # Film puanla (id, puan)
  python3 oneri.py --note 1 "Muhtesem"      # Film notu ekle
  python3 oneri.py --detail 1                # Film detayi
  python3 oneri.py --report                  # TXT rapor
  python3 oneri.py --stats                   # Istatistikler
  python3 oneri.py --import-anilist 10       # AniList import
  python3 oneri.py --web 8080                # Web arayuz
  python3 oneri.py --cli                     # Interaktif CLI
"""
import json, os, sys, sqlite3, argparse, urllib.request
from datetime import datetime
from collections import Counter

BASE = "/data/data/com.termux/files/home/anime-project"
DB_PATH = f"{BASE}/data/recommender.db"
TXT_DIR = f"{BASE}/output/txt"

# === TUR PROFILI (OWL zevk agirligi) ===
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
            synopsis TEXT DEFAULT '', duration INTEGER DEFAULT 0, episodes INTEGER DEFAULT 1,
            cover_url TEXT DEFAULT '', user_rating REAL DEFAULT 0, user_note TEXT DEFAULT '',
            format TEXT DEFAULT 'MOVIE', created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            watched_at TEXT DEFAULT ''
        );
        CREATE INDEX IF NOT EXISTS idx_fo ON films(owl_score DESC);
        CREATE INDEX IF NOT EXISTS idx_fw ON films(is_watched);
        CREATE INDEX IF NOT EXISTS idx_ft ON films(title_lower);
        CREATE INDEX IF NOT EXISTS idx_fy ON films(year);
        CREATE INDEX IF NOT EXISTS idx_fs ON films(user_rating DESC);
        CREATE INDEX IF NOT EXISTS idx_ff ON films(format);
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
          duration
          description
          coverImage { medium }
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
    for col, typ in [("synopsis","TEXT DEFAULT ''"),("duration","INTEGER DEFAULT 0"),
                      ("episodes","INTEGER DEFAULT 1"),("cover_url","TEXT DEFAULT ''"),
                      ("format","TEXT DEFAULT 'MOVIE'")]:
        try: db.execute("ALTER TABLE films ADD COLUMN %s %s" % (col, typ))
        except: pass
    db.commit()

    added = updated = 0
    for page in range(1, pages + 1):
        result = fetch_anilist(page)
        if not result or "data" not in result:
            print(f"Sayfa {page}: HATA")
            continue
        items = result["data"]["Page"]["media"]
        for m in items:
            title = m["title"]["romaji"] or m["title"]["english"] or "Unknown"
            tl = title.lower()
            year = m.get("startDate", {}).get("year") or 2000
            score = (m.get("meanScore") or 70) / 10
            genres = m.get("genres", [])
            studio = m["studios"]["nodes"][0]["name"] if m.get("studios", {}).get("nodes") else "Unknown"
            src_map = {"ORIGINAL":"Original","MANGA":"Manga","LIGHT_NOVEL":"Light Novel",
                       "NOVEL":"Novel","VISUAL_NOVEL":"Visual Novel","WEB_NOVEL":"Web Novel","GAME":"Game"}
            src = src_map.get(m.get("source",""), "Other")
            gj = json.dumps(genres)
            pop = m.get("popularity", 0)
            dur = m.get("duration", 0) or 0
            desc = (m.get("description") or "")[:600]
            cover = (m.get("coverImage") or {}).get("medium", "")
            fmt = m.get("format", "MOVIE")

            gb = sum(TASTE_W.get(g, 5) for g in genres) / max(len(genres), 1) * 0.05
            yb = 0.15 if year >= 2020 else (0.08 if year >= 2010 else 0.03)
            pb = 0.1 if pop > 1000 else (0.05 if pop > 500 else 0)
            ow = min(round(score + gb + yb + pb, 1), 10.0)

            try:
                db.execute("INSERT INTO films(title,title_lower,year,studio,mal_score,owl_score,source,genres,popularity,duration,synopsis,cover_url,format) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                           (title, tl, year, studio, score, ow, src, gj, pop, dur, desc, cover, fmt))
                added += 1
            except sqlite3.IntegrityError:
                db.execute("UPDATE films SET mal_score=?,owl_score=?,genres=?,popularity=?,duration=?,synopsis=?,cover_url=?,studio=?,source=?,format=? WHERE title_lower=?",
                           (score, ow, gj, pop, dur, desc, cover, studio, src, fmt, tl))
                updated += 1
        print(f"Sayfa {page}: {len(items)} film")
    db.commit()
    total = db.execute("SELECT COUNT(*) FROM films").fetchone()[0]
    print(f"\nEklenen: {added}, Guncellenen: {updated}, Toplam: {total}")
    return added + updated

# === IZLENEN ISLEMLERI ===
def mark_watched(film_id, rating=0):
    db = get_db()
    row = db.execute("SELECT title, title_lower, genres FROM films WHERE id=?", (film_id,)).fetchone()
    if not row:
        print(f"❌ Film bulunamadi: id={film_id}")
        return False
    tl = row["title_lower"]
    now = datetime.now().isoformat()
    db.execute("UPDATE films SET is_watched=1, watched_at=? WHERE id=?", (now, film_id))
    db.execute("INSERT OR REPLACE INTO watched(title_lower,title,watched_at,rating) VALUES(?,?,?,?)",
               (tl, row["title"], now, rating))
    for g in (json.loads(row["genres"]) if row["genres"] and row["genres"] != "[]" else []):
        db.execute("INSERT INTO taste_log(action,film_title,timestamp) VALUES(?,?,?)",
                   ("watched", tl, now))
    db.commit()
    n = db.execute("SELECT COUNT(*) FROM films WHERE is_watched=1").fetchone()[0]
    print(f"✅ '{row['title']}' izlendi (puan: {rating}). Toplam izlenen: {n}")
    return True

def rate_film(film_id, rating):
    db = get_db()
    row = db.execute("SELECT title FROM films WHERE id=?", (film_id,)).fetchone()
    if not row:
        print(f"❌ Film bulunamadi: id={film_id}")
        return False
    db.execute("UPDATE films SET user_rating=? WHERE id=?", (rating, film_id))
    db.commit()
    print(f"✅ '{row['title']}' puanlandi: {rating}/10")
    return True

def note_film(film_id, note):
    db = get_db()
    row = db.execute("SELECT title FROM films WHERE id=?", (film_id,)).fetchone()
    if not row:
        print(f"❌ Film bulunamadi: id={film_id}")
        return False
    db.execute("UPDATE films SET user_note=? WHERE id=?", (note, film_id))
    db.commit()
    t = row["title"]
    print(f"✅ '{t}' not eklendi: {note}")
    return True

# === ZEVK PROFILI ===
def get_taste_profile(db):
    watched = db.execute("SELECT f.genres, f.owl_score FROM films f WHERE f.is_watched=1").fetchall()
    genre_counts = Counter()
    genre_scores = Counter()
    for row in watched:
        genres_str = row["genres"]
        owl = row["owl_score"] or 7
        if genres_str and genres_str != "[]":
            for g in json.loads(genres_str):
                genre_counts[g] += 1
                genre_scores[g] += owl
    # Normalize scores
    avg_scores = {}
    for g in genre_counts:
        avg_scores[g] = genre_scores[g] / genre_counts[g]
    return genre_counts, avg_scores

def get_taste_weights(db):
    counts, avg_scores = get_taste_profile(db)
    if not counts:
        return TASTE_W
    weights = dict(TASTE_W)
    total = sum(counts.values())
    for genre, count in counts.items():
        ratio = count / total
        if ratio > 0.1:
            weights[genre] = weights.get(genre, 5) + 2
        elif ratio > 0.05:
            weights[genre] = weights.get(genre, 5) + 1
    return weights

# === ONERI ALGORITMASI v4 ===
def recommend(db, category=None, genre=None, studio=None, source=None,
              year_from=0, year_to=2030, min_score=0, max_score=10,
              format_type=None, unwatched_only=True, limit=20, smart=True):
    """
    v4 Oneri algoritmasi:
    1. Filtreler (tur/yil/kaynak/format/puan)
    2. OWL skoru (AniList + zevk + yil + popularity)
    3. Content-based zevk profili bonusu
    4. Cesitlilik filtresi (her turden max 3)
    5. Dengeli popularite (cok az/niye olanlarda bonus)
    """
    conditions = ["owl_score>=? AND year BETWEEN ? AND ?"]
    params = [min_score, year_from, year_to]
    
    if max_score < 10:
        conditions.append("owl_score<=?")
        params.append(max_score)
    if unwatched_only:
        conditions.append("is_watched=0")
    if source:
        conditions.append("source=?")
        params.append(source)
    if format_type:
        conditions.append("format=?")
        params.append(format_type)
    if studio:
        conditions.append("studio LIKE ?")
        params.append(f"%{studio}%")
    
    where = " AND ".join(conditions)
    q = f"SELECT * FROM films WHERE {where} ORDER BY owl_score DESC LIMIT ?"
    params.append(limit * 4)  # Fazla cek, sonra filtrele
    
    rows = db.execute(q, params).fetchall()
    if not rows:
        return []

    taste_weights = get_taste_weights(db) if smart else TASTE_W

    # Genre filtresi (post-query)
    if genre:
        genre_lower = genre.lower()
        rows = [r for r in rows if r["genres"] and genre_lower in r["genres"].lower()]

    # Category = source eslesmesi (geriye uyumluluk)
    if category and not genre:
        cat_lower = category.lower()
        rows = [r for r in rows if r["genres"] and cat_lower in r["genres"].lower()]

    # Puanla
    scored = []
    for row in rows:
        base = row["owl_score"]
        
        # Content-based bonus
        genres = json.loads(row["genres"]) if row["genres"] and row["genres"] != "[]" else []
        if genres:
            taste_bonus = sum(taste_weights.get(g, 5) for g in genres) / len(genres) * 0.12
        else:
            taste_bonus = 0
        
        # Kullanici puani bonusu (eger izlendiyse ve puan verildiyse)
        if row["user_rating"] > 0:
            user_bonus = (row["user_rating"] - 5) * 0.05
        else:
            user_bonus = 0
        
        # Recency bonus
        year = row["year"] or 2010
        if year >= 2023:
            recency = 0.1
        elif year >= 2018:
            recency = 0.05
        else:
            recency = 0
        
        # Popularity balance
        pop = row["popularity"] or 1
        if pop > 5000:
            pop_b = 0.08
        elif pop > 1000:
            pop_b = 0.12
        elif pop > 200:
            pop_b = 0.05
        else:
            pop_b = 0.03
        
        final = base + (taste_bonus + user_bonus + recency + pop_b) * 0.5
        scored.append((round(min(final, 10.0), 2), row))

    scored.sort(key=lambda x: x[0], reverse=True)

    # Cesitlilik filtresi: her turden max 3
    genre_count = Counter()
    diverse = []
    for score, row in scored:
        genres = json.loads(row["genres"]) if row["genres"] and row["genres"] != "[]" else []
        main = genres[0] if genres else "Other"
        if genre_count[main] < 3:
            diverse.append((score, row))
            genre_count[main] += 1
        if len(diverse) >= limit:
            break

    return diverse

# === FILM DETAY ===
def get_detail(db, film_id):
    row = db.execute("SELECT * FROM films WHERE id=?", (film_id,)).fetchone()
    if not row:
        return None
    return dict(row)

# === ARAMA ===
def search_film(db, query, limit=20):
    q = f"%{query.lower()}%"
    return db.execute(
        "SELECT id,title,year,owl_score,studio,genres,cover_url FROM films WHERE title_lower LIKE ? ORDER BY owl_score DESC LIMIT ?",
        (q, limit)).fetchall()

# === ISTATISTIKLER ===
def get_stats(db):
    total = db.execute("SELECT COUNT(*) FROM films").fetchone()[0]
    watched = db.execute("SELECT COUNT(*) FROM films WHERE is_watched=1").fetchone()[0]
    avg = db.execute("SELECT AVG(owl_score) FROM films WHERE is_watched=0").fetchone()[0]
    decades = db.execute("SELECT (year/10)*10 as d, COUNT(*) FROM films WHERE is_watched=0 GROUP BY d ORDER BY d").fetchall()
    sources = db.execute("SELECT source, COUNT(*) FROM films WHERE is_watched=0 GROUP BY source ORDER BY COUNT(*) DESC LIMIT 10").fetchall()
    studios = db.execute("SELECT studio, COUNT(*) FROM films WHERE is_watched=0 AND studio NOT IN ('Unknown','') GROUP BY studio ORDER BY COUNT(*) DESC LIMIT 10").fetchall()
    formats = db.execute("SELECT format, COUNT(*) FROM films GROUP BY format").fetchall()
    genres_all = db.execute("SELECT genres FROM films WHERE is_watched=0").fetchall()
    genre_counter = Counter()
    for row in genres_all:
        if row["genres"] and row["genres"] != "[]":
            for g in json.loads(row["genres"]):
                genre_counter[g] += 1
    taste_counts, taste_avg = get_taste_profile(db)
    return {
        "total": total, "watched": watched, "unwatched": total - watched,
        "avg_score": avg, "decades": decades, "sources": sources,
        "studios": studios, "formats": formats,
        "genre_ranking": genre_counter.most_common(15),
        "taste_profile": dict(taste_counts.most_common(10)),
        "taste_avg_scores": taste_avg,
    }

# === WEB ARAYUZ v4 ===
def start_web_server(port=8080):
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import urllib.parse, html as htmlmod

    db_conn = get_db()

    class Handler(BaseHTTPRequestHandler):
        def get_db(self):
            # Her istek icin fresh connection
            db = sqlite3.connect(DB_PATH)
            db.row_factory = sqlite3.Row
            return db

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            path = parsed.path

            if path == "/" or path == "/index":
                self._serve_index(params)
            elif path == "/film":
                film_id = int(params.get("id", [0])[0])
                self._serve_detail(film_id)
            elif path == "/api/recommend":
                self._api_recommend(params)
            elif path == "/api/search":
                self._api_search(params)
            elif path == "/api/stats":
                self._api_stats()
            elif path == "/api/dump":
                self._api_dump_all()
            else:
                self.send_response(404)
                self.end_headers()

        def _serve_index(self, params):
            db = self.get_db()
            limit = min(int(params.get("limit", [20])[0]), 100)
            genre_f = params.get("genre", [None])[0]
            source_f = params.get("source", [None])[0]
            studio_f = params.get("studio", [None])[0]
            yf = int(params.get("year_from", [0])[0])
            yt = int(params.get("year_to", [2030])[0])
            ms = float(params.get("min_score", [0])[0])
            search_q = params.get("q", [None])[0]

            if search_q:
                films = search_film(db, search_q, limit)
                scored = [(r["owl_score"], r) for r in films]
                scored.sort(key=lambda x: x[0], reverse=True)
            else:
                scored = recommend(db, genre=genre_f, source=source_f, studio=studio_f,
                                   year_from=yf, year_to=yt, min_score=ms, limit=limit)
            stats = get_stats(db)
            db.close()

            # Filtre secenekleri
            all_genres = sorted(set(g for _, r in scored for g in (json.loads(r["genres"]) if r["genres"] and r["genres"] != "[]" else [])))
            all_sources = sorted(set(r["source"] for _, r in scored if r["source"] != "Unknown"))

            genre_opts = "".join(f'<option value="{g}" {"selected" if g==genre_f else ""}>{g}</option>' for g in all_genres[:20])
            source_opts = "".join(f'<option value="{s}" {"selected" if s==source_f else ""}>{s}</option>' for s in all_sources)

            film_html = ""
            for i, (score, row) in enumerate(scored, 1):
                genres = json.loads(row["genres"]) if row["genres"] and row["genres"] != "[]" else []
                badges = "".join(f'<span class="badge">{g}</span>' for g in genres[:4])
                cover = row["cover_url"] or ""
                cover_html = f'<img src="{cover}" class="cover" loading="lazy" onerror="this.style.display=\'none\'">' if cover else '<div class="cover placeholder">🎬</div>'
                watched_class = "watched" if row["is_watched"] else ""
                user_r = f" | ⭐ {row['user_rating']}" if row["user_rating"] > 0 else ""
                film_html += f"""
                <a href="/film?id={row['id']}" class="film-card {watched_class}">
                    {cover_html}
                    <div class="film-info">
                        <div class="film-title">#{i} {htmlmod.escape(row["title"])}</div>
                        <div class="film-meta">{row["year"]} · {htmlmod.escape(row["studio"])} · {row["source"]}{user_r}</div>
                        <div class="film-score">{score}</div>
                        <div class="film-badges">{badges}</div>
                    </div>
                </a>"""

            content = f"""
            <div class="stats-bar">
                <span>📊 {stats["total"]} film</span>
                <span>✅ {stats["watched"]} izlenen</span>
                <span>📋 {stats["unwatched"]} kalan</span>
                <span>⭐ Ort: {stats["avg_score"]:.1f}</span>
            </div>
            <div class="filters">
                <form method="GET" action="/">
                    <div class="filter-row">
                        <input type="text" name="q" placeholder="🔍 Ara..." value="{htmlmod.escape(search_q or '')}" class="search-input">
                        <select name="genre"><option value="">Tüm Türler</option>{genre_opts}</select>
                        <select name="source"><option value="">Tüm Kaynaklar</option>{source_opts}</select>
                        <input type="number" name="year_from" placeholder="Yıl başlangıç" value="{yf if yf else ''}" class="year-input">
                        <input type="number" name="year_to" placeholder="Yıl bitiş" value="{yt if yt != 2030 else ''}" class="year-input">
                        <input type="number" name="min_score" placeholder="Min OWL" value="{ms if ms else ''}" step="0.5" class="score-input">
                        <button type="submit" class="btn">Filtrele</button>
                        <a href="/" class="btn btn-clear">Temizle</a>
                    </div>
                </form>
            </div>
            <div class="film-grid">{film_html}</div>
            """

            self._send_html("OWL Anime & Film Oneri", content, "index")

        def _serve_detail(self, film_id):
            db = self.get_db()
            film = get_detail(db, film_id)
            if not film:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Not found")
                return

            genres = json.loads(film["genres"]) if film["genres"] and film["genres"] != "[]" else []
            badges = "".join(f'<span class="badge">{g}</span>' for g in genres)
            cover = film["cover_url"] or ""
            cover_html = f'<img src="{cover}" class="detail-cover" onerror="this.parentElement.innerHTML=\'<div class=detail-cover-placeholder>🎬</div>\'">' if cover else '<div class="detail-cover-placeholder">🎬</div>'
            synopsis = htmlmod.escape(film["synopsis"] or "Özet yok.")
            watched = "✅ Izlenmis" if film["is_watched"] else "📋 Bekliyor"
            user_r = f"⭐ Kullanıcı: {film['user_rating']}/10" if film["user_rating"] > 0 else "Kullanıcı puanı yok"
            note = f'<div class="note">📝 {htmlmod.escape(film["user_note"])}</div>' if film["user_note"] else ""
            duration = f"{film['duration']} dk" if film["duration"] > 0 else "?"
            year = film["year"] or "?"

            content = f"""
            <a href="/" class="back-link">← Listeye Don</a>
            <div class="detail">
                <div class="detail-header">
                    {cover_html}
                    <div class="detail-info">
                        <h2>{htmlmod.escape(film["title"])}</h2>
                        <div class="detail-meta">
                            <span>{year}</span> · <span>{htmlmod.escape(film["studio"])}</span> · <span>{film["source"]}</span> · <span>{duration}</span>
                        </div>
                        <div class="detail-scores">
                            <span class="score-box owl">OWL: {film["owl_score"]}</span>
                            <span class="score-box mal">MAL: {film["mal_score"]:.1f}</span>
                            {f'<span class="score-box user">{user_r}</span>' if film["user_rating"] > 0 else ""}
                        </div>
                        <div class="detail-badges">{badges}</div>
                        <div class="detail-status">{watched}</div>
                    </div>
                </div>
                <div class="detail-synopsis">
                    <h3>Ozet</h3>
                    <p>{synopsis}</p>
                </div>
                {note}
            </div>
            """
            self._send_html(film["title"], content, "detail")
            db.close()

        def _api_recommend(self, params):
            db = self.get_db()
            limit = min(int(params.get("limit", [20])[0]), 100)
            genre_f = params.get("genre", [None])[0]
            source_f = params.get("source", [None])[0]
            ms = float(params.get("min_score", [0])[0])
            yf = int(params.get("year_from", [0])[0])
            yt = int(params.get("year_to", [2030])[0])
            films = recommend(db, genre=genre_f, source=source_f, min_score=ms, year_from=yf, year_to=yt, limit=limit)
            result = []
            for score, r in films:
                result.append({
                    "id": r["id"], "title": r["title"], "year": r["year"],
                    "score": score, "owl_score": r["owl_score"], "studio": r["studio"],
                    "source": r["source"], "genres": json.loads(r["genres"]) if r["genres"] and r["genres"] != "[]" else [],
                    "cover_url": r["cover_url"], "synopsis": r["synopsis"],
                    "is_watched": bool(r["is_watched"]), "user_rating": r["user_rating"],
                })
            db.close()
            self._send_json(result)

        def _api_search(self, params):
            db = self.get_db()
            q = params.get("q", [""])[0]
            limit = min(int(params.get("limit", [20])[0]), 100)
            if not q:
                self._send_json([])
                return
            rows = search_film(db, q, limit)
            result = [{"id": r["id"], "title": r["title"], "year": r["year"], "score": r["owl_score"], "studio": r["studio"], "genres": json.loads(r["genres"]) if r["genres"] and r["genres"] != "[]" else [], "cover_url": r["cover_url"]} for r in rows]
            db.close()
            self._send_json(result)

        def _api_stats(self):
            db = self.get_db()
            s = get_stats(db)
            db.close()
            r = {
                "total": s["total"], "watched": s["watched"], "unwatched": s["unwatched"],
                "avg_score": round(s["avg_score"] or 0, 1),
                "formats": {},
                "top_genres": {g: c for g, c in s["genre_ranking"][:10]},
                "top_studios": {},
                "taste_profile": s["taste_profile"],
            }
            for row in s["formats"]:
                r["formats"][row[0]] = row[1]
            for row in s["studios"][:10]:
                r["top_studios"][row[0]] = row[1]
            self._send_json(r)

        def _api_dump_all(self):
            db = self.get_db()
            rows = db.execute("SELECT id, title, year, owl_score, studio, source, genres, cover_url, is_watched FROM films ORDER BY owl_score DESC").fetchall()
            result = [{"id": r["id"], "title": r["title"], "year": r["year"], "score": r["owl_score"], "studio": r["studio"], "source": r["source"], "genres": json.loads(r["genres"]) if r["genres"] and r["genres"] != "[]" else [], "cover_url": r["cover_url"], "is_watched": bool(r["is_watched"])} for r in rows]
            db.close()
            self._send_json(result)

        def _send_html(self, title, content, page="index"):
            head = ""
            if page != "detail":
                head = '<a href="/" class="logo-link"><h1>◇ OWL Anime & Film Oneri</h1></a>'
            else:
                head = '<div class="logo-sm"><a href="/">◇ OWL</a></div>'
            full = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{htmlmod.escape(title)}</title>
<style>
:root {{
  --bg: #0c0c14; --surface: #14141e; --border: #1e1e2e;
  --text: #e2e8f0; --muted: #64748b; --purple: #a855f7; --purple-dim: #6b21a8;
  --blue: #0ea5e9; --green: #22c55e; --yellow: #eab308;
  --radius: 10px; --gap: 12px;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
  background: var(--bg); color: var(--text);
  padding: 16px; line-height: 1.5;
}}
h1 {{ color: var(--purple); font-size: 1.3em; margin-bottom: 4px; }}
h2 {{ color: var(--text); font-size: 1.4em; margin-bottom: 4px; }}
h3 {{ color: var(--muted); font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }}
.logo-link {{ text-decoration: none; }}
.logo-sm a {{ color: var(--purple); text-decoration: none; font-size: 1.1em; font-weight: 700; }}
.stats-bar {{
  display: flex; flex-wrap: wrap; gap: 12px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 10px 14px; margin-bottom: var(--gap);
  font-size: 0.85em; color: var(--muted);
}}
.filters {{
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 12px; margin-bottom: var(--gap);
}}
.filter-row {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
.filter-row input, .filter-row select {{
  background: var(--bg); border: 1px solid var(--border); color: var(--text);
  border-radius: 6px; padding: 6px 10px; font-size: 0.85em;
}}
.search-input {{ flex: 1; min-width: 160px; }}
.year-input {{ width: 90px; }}
.score-input {{ width: 70px; }}
select {{ min-width: 120px; }}
.btn {{
  background: var(--purple-dim); color: var(--text); border: none;
  border-radius: 6px; padding: 6px 14px; font-size: 0.85em;
  cursor: pointer; text-decoration: none; display: inline-block;
}}
.btn:hover {{ background: var(--purple); }}
.btn-clear {{ background: transparent; border: 1px solid var(--border); }}
.film-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--gap);
}}
.film-card {{
  display: flex; gap: 10px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 12px;
  text-decoration: none; color: inherit;
  transition: border-color 0.2s;
}}
.film-card:hover {{ border-color: var(--purple); }}
.film-card.watched {{ opacity: 0.6; }}
.cover {{
  width: 80px; height: 110px; object-fit: cover;
  border-radius: 6px; flex-shrink: 0;
}}
.cover.placeholder {{
  width: 80px; height: 110px; background: var(--border);
  border-radius: 6px; display: flex; align-items: center; justify-content: center;
  font-size: 1.8em; flex-shrink: 0;
}}
.film-info {{ flex: 1; min-width: 0; }}
.film-title {{ font-weight: 600; font-size: 0.95em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.film-meta {{ color: var(--muted); font-size: 0.78em; margin-top: 2px; }}
.film-score {{
  display: inline-block; background: var(--purple-dim);
  color: var(--text); font-weight: 700; font-size: 0.85em;
  padding: 2px 8px; border-radius: 4px; margin-top: 4px;
}}
.film-badges {{ margin-top: 4px; }}
.badge {{
  display: inline-block; background: rgba(14,165,233,0.12);
  color: var(--blue); padding: 1px 6px; border-radius: 4px;
  font-size: 0.7em; margin: 2px 3px 0 0;
}}
.detail {{ max-width: 800px; margin: 0 auto; }}
.back-link {{
  display: inline-block; color: var(--muted); text-decoration: none;
  font-size: 0.85em; margin-bottom: 16px;
}}
.back-link:hover {{ color: var(--purple); }}
.detail-header {{
  display: flex; gap: 20px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 20px; margin-bottom: 16px;
}}
.detail-cover {{
  width: 180px; height: 260px; object-fit: cover;
  border-radius: 8px; flex-shrink: 0;
}}
.detail-cover-placeholder {{
  width: 180px; height: 260px; background: var(--border);
  border-radius: 8px; display: flex; align-items: center; justify-content: center;
  font-size: 3em; flex-shrink: 0;
}}
.detail-info {{ flex: 1; }}
.detail-meta {{ color: var(--muted); font-size: 0.85em; margin: 8px 0; }}
.detail-meta span {{ margin-right: 8px; }}
.detail-scores {{ display: flex; gap: 8px; margin: 12px 0; }}
.score-box {{
  padding: 4px 10px; border-radius: 6px; font-size: 0.85em; font-weight: 600;
}}
.score-box.owl {{ background: var(--purple-dim); }}
.score-box.mal {{ background: rgba(34,197,94,0.15); color: var(--green); }}
.score-box.user {{ background: rgba(234,179,8,0.15); color: var(--yellow); }}
.detail-badges {{ margin: 8px 0; }}
.detail-status {{ color: var(--muted); font-size: 0.85em; margin-top: 8px; }}
.detail-synopsis {{
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 20px;
}}
.detail-synopsis p {{ color: var(--muted); line-height: 1.7; font-size: 0.9em; margin-top: 8px; }}
.note {{
  background: rgba(234,179,8,0.08); border: 1px solid rgba(234,179,8,0.2);
  border-radius: var(--radius); padding: 14px; margin-top: 12px;
  color: var(--text); font-size: 0.9em;
}}
@media (max-width: 600px) {{
  .film-grid {{ grid-template-columns: 1fr; }}
  .detail-header {{ flex-direction: column; align-items: center; }}
  .detail-cover, .detail-cover-placeholder {{ width: 140px; height: 200px; }}
  .filter-row {{ flex-direction: column; }}
  .filter-row input, .filter-row select {{ width: 100%; }}
}}
</style>
</head>
<body>
{head}
{content}
<div style="text-align:center;color:var(--muted);font-size:0.75em;margin-top:30px">
  OWL Oneri Motoru v4.0 · {datetime.now().strftime("%Y-%m-%d")}
</div>
</body>
</html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(full.encode())

        def _send_json(self, data):
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

        def log_message(self, format, *args):
            pass

    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"🌐 Web server baslatildi: http://localhost:{port}")
    print(f"   API: http://localhost:{port}/api/recommend")
    print(f"   Arama: http://localhost:{port}/api/search?q=yourname")
    server.serve_forever()

# === TXT RAPOR ===
def gen_report(db):
    os.makedirs(TXT_DIR, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    films = recommend(db, limit=500)
    with open(f"{TXT_DIR}/01_ana_liste.txt", "w", encoding="utf-8") as f:
        f.write(f"OWL ANIME & FILM ONERI LISTESI v4.0\nTarih: {now}\nToplam: {len(films)} oneri\n{'='*80}\n\n")
        for i, (score, row) in enumerate(films, 1):
            genres = json.loads(row["genres"]) if row["genres"] and row["genres"] != "[]" else []
            f.write(f"#{i:04d} | OWL:{score:.1f} | {row['title']} ({row['year']}) | {row['studio']} | {row['source']} | {', '.join(genres[:3])}\n")

    stats = get_stats(db)
    with open(f"{TXT_DIR}/02_stats.txt", "w", encoding="utf-8") as f:
        f.write(f"OWL ANIME & FILM ONERI SISTEMI v4.0 - ISTATISTIKLER\n{'='*80}\n\n")
        f.write(f"Toplam film: {stats['total']}\nIzlenen: {stats['watched']}\nKalan: {stats['unwatched']}\nOrt OWL skoru: {stats['avg_score']:.1f}\n\n")
        f.write("Yil dagilimi:\n")
        for d, c in stats["decades"]:
            f.write(f"  {d}s: {'█'*min(c,50)} ({c})\n")
        f.write("\nKaynak dagilimi:\n")
        for s, c in stats["sources"]:
            f.write(f"  {s}: {c}\n")
        f.write("\nEn iyi studyolar:\n")
        for s, c in stats["studios"]:
            f.write(f"  {s}: {c} film\n")
        f.write("\nTur dagilimi:\n")
        for g, c in stats["genre_ranking"][:15]:
            f.write(f"  {g}: {c}\n")
        if stats["taste_profile"]:
            f.write("\nZevk profilin (izlediklerine gore):\n")
            for g, c in stats["taste_profile"].items():
                avg = stats["taste_avg_scores"].get(g, 0)
                f.write(f"  {g}: {c} film (ort puan: {avg:.1f})\n")

    return len(films)

# === CLI ===
def interactive(db):
    print("\n  OWL ANIME & FILM ONERI SISTEMI v4.0")
    print(f"  {db.execute('SELECT COUNT(*) FROM films').fetchone()[0]} film yuklu")
    print("="*50)
    while True:
        print("\n[K]Oneri [T]Tur [G]Genre [Y]Yil [P]Puan [W]Izledi [R]Rapor [S]Ara [I]Stats [D]Detay [U]Web [Q]Cikis")
        c = input("Secim: ").strip().lower()
        if c == "q":
            break
        elif c == "k":
            films = recommend(db, limit=15)
            for i, (s, f) in enumerate(films, 1):
                genres = json.loads(f["genres"]) if f["genres"] and f["genres"] != "[]" else []
                print(f"  {i:2d}.[{s:.1f}] {f['title']} ({f['year']}) - {f['studio']} | {','.join(genres[:2])}")
        elif c == "t":
            stats = get_stats(db)
            print("  Turler:")
            for g, cnt in stats["genre_ranking"][:15]:
                print(f"    {g}: {cnt}")
        elif c == "g":
            g = input("Tur ara: ").strip()
            if g:
                films = recommend(db, genre=g, limit=15)
                for i, (s, f) in enumerate(films, 1):
                    print(f"  {i:2d}.[{s:.1f}] {f['title']} ({f['year']}) - {f['studio']}")
        elif c == "i":
            stats = get_stats(db)
            print(f"  Toplam:{stats['total']} Izlenen:{stats['watched']} Kalan:{stats['unwatched']} Ort:{stats['avg_score']:.1f}")
            if stats["taste_profile"]:
                print("  Zevk:", ", ".join(f"{g}:{c}" for g, c in list(stats["taste_profile"].items())[:5]))
        elif c == "w":
            try:
                fid = int(input("Film ID: "))
                rating = float(input("Puan (0=yok): ") or "0")
                mark_watched(fid, rating)
            except:
                print("  Gecersiz giris.")
        elif c == "d":
            try:
                fid = int(input("Film ID: "))
                film = get_detail(db, fid)
                if film:
                    genres = json.loads(film["genres"]) if film["genres"] and film["genres"] != "[]" else []
                    print(f"\n  {film['title']} ({film['year']})")
                    print(f"  Studio: {film['studio']} | Kaynak: {film['source']}")
                    print(f"  OWL: {film['owl_score']} | MAL: {film['mal_score']:.1f}")
                    print(f"  Tur: {', '.join(genres)}")
                    print(f"  Ozet: {(film['synopsis'] or 'Yok')[:200]}")
                else:
                    print("  Film bulunamadi.")
            except:
                print("  Gecersiz giris.")
        elif c == "r":
            n = gen_report(db)
            print(f"  Rapor olusturuldu: {n} film -> {TXT_DIR}/")
        elif c == "s":
            q = input("Ara: ").strip()
            if q:
                r = search_film(db, q)
                for f in r:
                    print(f"  [{f['owl_score']}] {f['title']} ({f['year']}) - {f['studio']}")
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
                    print(f"  {i:2d}.[{s:.1f}] {f['title']} ({f['year']})")
            except:
                pass
        elif c == "p":
            try:
                ms = float(input("Min OWL:"))
                films = recommend(db, min_score=ms, limit=15)
                for i, (s, f) in enumerate(films, 1):
                    print(f"  {i:2d}.[{s:.1f}] {f['title']} ({f['year']})")
            except:
                pass

# === ANA ===
def main():
    p = argparse.ArgumentParser(description="OWL Anime & Film Oneri v4.0")
    p.add_argument("--cli", action="store_true")
    p.add_argument("--recommend", type=int, default=0)
    p.add_argument("--category", type=str, help="Kategori (genre ile ayni)")
    p.add_argument("--genre", type=str, help="Tur filtresi")
    p.add_argument("--studio", type=str, help="Studio filtresi")
    p.add_argument("--source", type=str, help="Kaynak filtresi (Manga, Original, etc)")
    p.add_argument("--year-from", type=int, default=0)
    p.add_argument("--year-to", type=int, default=2030)
    p.add_argument("--min-score", type=float, default=0)
    p.add_argument("--max-score", type=float, default=10)
    p.add_argument("--format", type=str, help="Format (MOVIE, TV, OVA)")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--watched", action="store_true", help="Sadece izlenmemisleri goster")
    p.add_argument("--report", action="store_true")
    p.add_argument("--stats", action="store_true")
    p.add_argument("--search", type=str)
    p.add_argument("--watch", type=int, help="Film ID ile izle")
    p.add_argument("--rate", type=float, help="Film puankla (--watch ile veya --rate ID)")
    p.add_argument("--note", type=str, help="Film notu ekle")
    p.add_argument("--detail", type=int, help="Film detay (ID)")
    p.add_argument("--import-anilist", type=int, default=0)
    p.add_argument("--web", type=int, default=0)
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
        print(f"Toplam: {stats['total']}")
        print(f"Izlenen: {stats['watched']}")
        print(f"Kalan: {stats['unwatched']}")
        print(f"Ort OWL: {stats['avg_score']:.1f}")
        print(f"\nYil dagilimi:")
        for d, c in stats["decades"]:
            print(f"  {d}s: {'█'*min(c,40)} ({c})")
        print(f"\nKaynaklar:")
        for s, c in stats["sources"][:5]:
            print(f"  {s}: {c}")
        print(f"\nTurler:")
        for g, c in stats["genre_ranking"][:10]:
            print(f"  {g}: {c}")
        print(f"\nStudyolar:")
        for s, c in stats["studios"][:5]:
            print(f"  {s}: {c}")
        if stats["taste_profile"]:
            print(f"\nZevk profili:")
            for g, c in stats["taste_profile"].items():
                avg = stats["taste_avg_scores"].get(g, 0)
                print(f"  {g}: {c} film (ort: {avg:.1f})")
        return

    if args.search:
        r = search_film(db, args.search)
        for f in r:
            genres = json.loads(f["genres"]) if f["genres"] and f["genres"] != "[]" else []
            print(f"[{f['owl_score']}] {f['title']} ({f['year']}) - {f['studio']} | {','.join(genres[:3])}")
        return

    if args.watch:
        rating = args.rate if args.rate else 0
        mark_watched(args.watch, rating)
        return

    if args.rate and not args.watch:
        # --rate PUAN --detail ID seklinde kullanilabilir
        print("Kullanim: --watch ID --rate PUAN")
        return

    if args.note:
        print("Kullanim: --watch ID --note NOT")
        return

    if args.detail:
        film = get_detail(db, args.detail)
        if film:
            genres = json.loads(film["genres"]) if film["genres"] and film["genres"] != "[]" else []
            print(f"\n{film['title']} ({film['year']})")
            print(f"  Studio: {film['studio']}")
            print(f"  Kaynak: {film['source']}")
            print(f"  Format: {film['format']}")
            print(f"  OWL: {film['owl_score']} | MAL: {film['mal_score']:.1f} | IMDB: {film['imdb_score']:.1f}")
            print(f"  Tur: {', '.join(genres)}")
            print(f"  Populerite: {film['popularity']}")
            print(f"  Sure: {film['duration']} dk")
            print(f"  Izlenmis: {'Evet' if film['is_watched'] else 'Hayir'}")
            print(f"  Kullanici puani: {film['user_rating'] or 'Yok'}")
            print(f"\n  Ozet:\n  {(film['synopsis'] or 'Yok')[:400]}")
        else:
            print("Film bulunamadi.")
        return

    if args.report:
        n = gen_report(db)
        print(f"Rapor: {n} film -> {TXT_DIR}/")
        return

    if args.recommend > 0 or (not args.cli and not args.detail and not args.watch):
        cat = args.category or args.genre
        films = recommend(db, category=cat, genre=args.genre, studio=args.studio,
                          source=args.source, year_from=args.year_from, year_to=args.year_to,
                          min_score=args.min_score, max_score=args.max_score,
                          format_type=args.format, unwatched_only=not args.watched,
                          limit=args.recommend if args.recommend > 0 else 10)
        if not films:
            print("Kriterlere uygun film bulunamadi.")
            return
        print(f"\nOWL Size {len(films)} Film Oneriyor:\n")
        for i, (s, f) in enumerate(films, 1):
            genres = json.loads(f["genres"]) if f["genres"] and f["genres"] != "[]" else []
            print(f"  {i:2d}.[{s:.1f}] {f['title']} ({f['year']}) - {f['studio']} | {','.join(genres[:3])}")
        return

    if args.cli:
        interactive(db)
        return

if __name__ == "__main__":
    main()
