#!/usr/bin/env python3
"""
OWL Anime & Film Oneri Sistemi v5.0
- 602 film (AniList API + manuel)
- Content-based collaborative filtering
- Tur/yil/kaynak/format/puan filtresi
- Kullanici puani ve not sistemi
- Modern web arayuzu (responsive, arama, detay sayfasi, watchlist, profil)
- JSON API (REST-like) + watchlist API + profil API + export API
- CLI arayuz
- OMDb API ile IMDB skoru cekme
- CSV/PDF export
- Fonksiyon API (build.py ve diger moduller icin import edilebilir)

Kullanim:
  python3 oneri.py                          # Varsayilan: 10 oneri
  python3 oneri.py --recommend 20           # 20 oneri
  python3 oneri.py --genre Psychological    # Tur filtresi
  python3 oneri.py --studio "Studio Ghibli" # Studio filtresi
  python3 oneri.py --source Manga            # Kaynak filtresi
  python3 oneri.py --min-score 8.5           # Min OWL puani
  python3 oneri.py --year-from 2020          # Yil filtresi
  python3 oneri.py --search "your name"      # Arama
  python3 oneri.py --watch 1 --rate 9.5     # Film izle + puanla
  python3 oneri.py --watch 1 --note "mukemmel" # Film notu
  python3 oneri.py --detail 1                # Film detayi
  python3 oneri.py --report                  # TXT rapor
  python3 oneri.py --stats                   # Istatistikler
  python3 oneri.py --import-anilist 10       # AniList import
  python3 oneri.py --web 8080                # Web arayuz
  python3 oneri.py --cli                     # Interaktif CLI
  python3 oneri.py --fetch-imdb              # OMDb ile IMDB skorlarini cek
  python3 oneri.py --export csv              # CSV export
  python3 oneri.py --compare 1,2,3          # Film karsilastirma
  python3 oneri.py --profile                 # Kullanici profili (CLI)

Modul olarak kullanim:
  from oneri import init_db, recommend, get_stats, mark_watched, rate_film
  from oneri import import_anilist_data, search_film, get_detail
  from oneri import fetch_imdb_scores, export_csv, compare_films
"""
import json, os, sys, sqlite3, argparse, urllib.request, re, csv, io
from datetime import datetime
from collections import Counter

# === ECHO HTML TEMPLATE ===
_ECHO_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
<meta name="theme-color" content="#0a0a0f">
<title>{page_title}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&display=swap');
:root{{
  --bg:#0a0a0f;--surface:#111114;--border:#1a1a1e;--border2:#222228;
  --text:#c8c8c8;--muted:#555566;
  --accent:#6b5b95;--accent2:#4a4a6a;
  --glow:rgba(107,91,149,0.15);
  --radius:6px;--gap:10px;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{height:100%}}
body{{font-family:'Space Grotesk',system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.6;font-weight:300}}
body::before{{content:'';position:fixed;top:0;left:0;right:0;bottom:0;background:repeating-linear-gradient(0deg,rgba(0,0,0,0.02) 0px,rgba(0,0,0,0.02) 1px,transparent 1px,transparent 3px);pointer-events:none;z-index:9999;opacity:0.3}}
@keyframes fadeInUp{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes pulseGlow{{0%,100%{{opacity:0.4}}50%{{opacity:1}}}}
@keyframes glitch{{0%,100%{{transform:translate(0)}}20%{{transform:translate(-1px,1px)}}40%{{transform:translate(1px,-1px)}}60%{{transform:translate(-1px,-1px)}}80%{{transform:translate(1px,1px)}}}}
.topbar{{position:sticky;top:0;z-index:100;background:rgba(10,10,15,0.92);backdrop-filter:blur(10px);border-bottom:1px solid var(--border);padding:10px 16px;display:flex;align-items:center;gap:10px}}
.topbar .logo{{font-size:0.95em;font-weight:600;letter-spacing:0.2em;color:var(--text);text-decoration:none;display:flex;align-items:center;gap:8px;opacity:0.85}}
.topbar .logo:hover{{opacity:1;animation:glitch 0.2s}}
.logo-symbol{{width:20px;height:20px;position:relative;display:inline-block}}
.logo-symbol svg{{width:100%;height:100%}}
.logo-dot{{width:3px;height:3px;background:var(--accent);border-radius:50%;position:absolute;top:1px;right:1px;animation:pulseGlow 3s ease-in-out infinite}}
.topbar .badge{{background:var(--accent);color:#fff;font-size:0.5em;padding:2px 6px;border-radius:3px;font-weight:600;letter-spacing:0.1em;opacity:0.7}}
.bottom-nav{{position:fixed;bottom:0;left:0;right:0;z-index:100;background:rgba(10,10,15,0.92);backdrop-filter:blur(10px);border-top:1px solid var(--border);display:flex;justify-content:space-around;padding:6px 0;padding-bottom:max(6px,env(safe-area-inset-bottom))}}
.bn-item{{display:flex;flex-direction:column;align-items:center;gap:2px;text-decoration:none;color:var(--muted);font-size:0.55em;padding:4px 10px;border-radius:4px;transition:all 0.15s;letter-spacing:0.05em}}
.bn-item:hover,.bn-item.active{{color:var(--accent)}}
.bn-item .bn-icon{{font-size:1.2em}}
.main{{padding:14px;padding-bottom:70px;animation:fadeInUp 0.25s ease}}
.stats-bar{{display:flex;flex-wrap:wrap;gap:6px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:8px 12px;margin-bottom:var(--gap);font-size:0.7em;color:var(--muted)}}
.type-toggle{{display:flex;gap:4px;margin-bottom:var(--gap);flex-wrap:wrap}}
.type-toggle .btn{{flex:1;text-align:center;min-width:60px;font-size:0.68em;padding:5px 8px;background:var(--surface);color:var(--muted);border:1px solid var(--border)}}
.type-toggle .btn:hover{{background:var(--accent);color:#fff;border-color:var(--accent)}}
.filters{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:10px;margin-bottom:var(--gap)}}
.filter-row{{display:flex;flex-wrap:wrap;gap:6px;align-items:center}}
.filter-row input,.filter-row select{{background:var(--bg);border:1px solid var(--border);color:var(--text);border-radius:4px;padding:6px 10px;font-size:0.8em;font-weight:300}}
.search-input{{flex:1;min-width:120px}}.year-input{{width:70px}}.score-input{{width:55px}}select{{min-width:90px}}
.btn{{background:var(--surface);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:6px 12px;font-size:0.75em;cursor:pointer;text-decoration:none;display:inline-block;font-weight:400;transition:all 0.15s}}
.btn:hover{{background:var(--accent);color:#fff;border-color:var(--accent)}}.btn-sm{{padding:4px 8px;font-size:0.65em}}
.film-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:var(--gap)}}
.film-card{{display:flex;gap:10px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:10px;text-decoration:none;color:inherit;transition:all 0.15s}}
.film-card:hover{{border-color:var(--accent2);background:var(--glow)}}.film-card.watched{{opacity:0.35}}
.cover{{width:60px;height:85px;object-fit:cover;border-radius:4px;flex-shrink:0}}
.cover.placeholder{{width:60px;height:85px;background:var(--bg);border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:1.2em;flex-shrink:0;border:1px solid var(--border);color:var(--muted);opacity:0.5}}
.film-info{{flex:1;min-width:0}}.film-title{{font-weight:400;font-size:0.82em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--text);opacity:0.9}}
.film-meta{{color:var(--muted);font-size:0.62em;margin-top:2px;letter-spacing:0.03em}}
.film-score{{display:inline-block;background:var(--accent);color:#fff;font-weight:600;font-size:0.68em;padding:1px 6px;border-radius:3px;margin-top:3px;opacity:0.8}}
.film-badges{{margin-top:3px}}
.badge{{display:inline-block;background:transparent;color:var(--muted);padding:1px 5px;border-radius:3px;font-size:0.55em;margin:1px 1px 0 0;border:1px solid var(--border);letter-spacing:0.03em}}
.badge.mt{{color:var(--accent);border-color:var(--accent2)}}
.progress-bar{{height:2px;background:var(--border);border-radius:1px;margin-top:4px;overflow:hidden}}
.progress-fill{{height:100%;background:var(--accent);border-radius:1px;transition:width 0.3s}}
.progress-text{{font-size:0.55em;color:var(--muted);margin-top:1px;display:block}}
.detail{{max-width:700px;margin:0 auto}}.back-link{{display:inline-block;color:var(--muted);text-decoration:none;font-size:0.72em;margin-bottom:10px;letter-spacing:0.05em}}
.back-link:hover{{color:var(--accent)}}
.detail-header{{display:flex;gap:14px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:14px;margin-bottom:var(--gap)}}
.detail-cover{{width:120px;height:170px;object-fit:cover;border-radius:6px;flex-shrink:0}}
.detail-cover-placeholder{{width:120px;height:170px;background:var(--bg);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:1.8em;flex-shrink:0;border:1px solid var(--border);color:var(--muted);opacity:0.4}}
.detail-info h2{{font-size:1em;margin-bottom:3px;color:var(--text);font-weight:400;letter-spacing:0.03em}}
.detail-meta{{color:var(--muted);font-size:0.7em;margin:5px 0;letter-spacing:0.03em}}
.detail-scores{{display:flex;gap:5px;margin:8px 0;flex-wrap:wrap}}
.score-box{{padding:3px 8px;border-radius:3px;font-size:0.68em;font-weight:600;opacity:0.8}}
.score-box.owl{{background:var(--accent);color:#fff}}
.score-box.mal{{background:transparent;color:var(--muted);border:1px solid var(--border)}}
.detail-badges{{margin:6px 0}}.detail-actions{{display:flex;gap:6px;margin-top:10px;flex-wrap:wrap}}
.detail-synopsis{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:14px;margin-bottom:var(--gap)}}
.detail-synopsis h3{{font-size:0.72em;color:var(--muted);margin-bottom:6px;letter-spacing:0.08em;text-transform:uppercase}}
.detail-synopsis p{{color:var(--muted);line-height:1.7;font-size:0.78em;font-weight:300}}
.note{{background:var(--glow);border:1px solid var(--border);border-radius:var(--radius);padding:10px;margin-top:8px;color:var(--text);font-size:0.75em;font-weight:300}}
.wl-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:var(--gap)}}
.wl-card{{display:flex;align-items:flex-start;gap:8px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:10px;position:relative}}
.wl-main{{display:flex;gap:8px;flex:1;text-decoration:none;color:inherit}}
.wl-info{{flex:1;min-width:0}}.wl-title{{font-weight:400;font-size:0.82em;color:var(--text)}}
.wl-meta{{color:var(--muted);font-size:0.62em;margin-top:2px}}
.wl-remove{{color:var(--muted);text-decoration:none;font-size:0.8em;padding:3px 6px;border-radius:3px}}
.wl-remove:hover{{color:var(--red);background:rgba(239,68,68,0.06)}}
.profile-stats{{display:flex;flex-wrap:wrap;gap:6px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:12px;margin-bottom:var(--gap)}}
.profile-stat{{display:flex;flex-direction:column;align-items:center;min-width:50px}}
.ps-num{{font-size:1em;font-weight:600;color:var(--text);opacity:0.8}}
.ps-lbl{{font-size:0.5em;color:var(--muted);margin-top:2px;letter-spacing:0.05em}}
.profile-sections{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:var(--gap);margin-bottom:var(--gap)}}
.prof-section{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:12px}}
.prof-section h3{{font-size:0.72em;margin-bottom:6px;color:var(--text);letter-spacing:0.06em;text-transform:uppercase;font-weight:400}}
.prof-list{{list-style:none;padding:0}}.prof-list li{{display:flex;justify-content:space-between;padding:3px 0;font-size:0.68em;border-bottom:1px solid var(--border);color:var(--muted)}}
.bar-chart{{display:flex;flex-direction:column;gap:5px}}.bar-row{{display:flex;align-items:center;gap:6px}}
.bar-label{{width:75px;font-size:0.6em;color:var(--muted);text-align:right;flex-shrink:0}}
.bar-track{{flex:1;height:8px;background:var(--border);border-radius:2px;overflow:hidden}}
.bar-fill{{height:100%;background:var(--accent);border-radius:2px;transition:width 0.4s ease;opacity:0.6}}
.bar-val{{width:15px;font-size:0.6em;color:var(--muted);text-align:right}}
.history-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:6px}}
.history-card{{display:flex;gap:6px;background:var(--surface);border:1px solid var(--border);border-radius:4px;padding:6px;text-decoration:none;color:inherit}}
.history-card:hover{{border-color:var(--accent2)}}
.cover-sm{{width:28px;height:40px;object-fit:cover;border-radius:2px;flex-shrink:0}}
.cover-sm.placeholder{{width:28px;height:40px;background:var(--bg);border-radius:2px;display:flex;align-items:center;justify-content:center;font-size:0.7em;flex-shrink:0;border:1px solid var(--border);color:var(--muted);opacity:0.4}}
.history-title{{font-size:0.65em;font-weight:400;color:var(--text)}}
.history-meta{{font-size:0.55em;color:var(--muted)}}.history-date{{font-size:0.5em;color:var(--muted);margin-top:1px}}
.empty-state{{text-align:center;padding:30px;color:var(--muted);font-size:0.75em;font-weight:300}}
.muted{{color:var(--muted)}}h2{{font-size:1em;margin-bottom:6px;color:var(--text);font-weight:400;letter-spacing:0.03em}}
h3{{font-size:0.72em;color:var(--muted);text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;font-weight:400}}
@media(max-width:600px){{
  .film-grid{{grid-template-columns:1fr}}.wl-grid{{grid-template-columns:1fr}}
  .detail-header{{flex-direction:column;align-items:center}}
  .detail-cover,.detail-cover-placeholder{{width:100px;height:140px}}
  .filter-row{{flex-direction:column}}.filter-row input,.filter-row select{{width:100%}}
  .profile-sections{{grid-template-columns:1fr}}.history-grid{{grid-template-columns:1fr}}
  .topbar{{padding:8px 12px}}.main{{padding:10px;padding-bottom:70px}}
}}
</style>
</head>
<body>
<div class="topbar">
  <a href="/" class="logo">
    <span class="logo-symbol">
      <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="16" cy="16" r="14" stroke="var(--accent)" stroke-width="1" opacity="0.2" stroke-dasharray="2 2"/>
        <circle cx="16" cy="16" r="11" stroke="var(--text)" stroke-width="1.2" opacity="0.4" stroke-dasharray="3 2"/>
        <path d="M16 16 L26 6" stroke="var(--text)" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/>
        <circle cx="16" cy="16" r="3.5" fill="var(--accent)" opacity="0.5"/>
        <circle cx="26" cy="6" r="2" fill="var(--text)" opacity="0.7"/>
      </svg>
      <span class="logo-dot"></span>
    </span>
    <span class="logo-text">ECHO</span>
  </a>
  <span class="badge">v5.2</span>
</div>
<div class="main">
{content}
</div>
<nav class="bottom-nav">
{nav_html}
</nav>
</body>
</html>"""
BASE = os.environ.get("ANIME_BASE", os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE, "data", "recommender.db")
TXT_DIR = os.path.join(BASE, "output", "txt")
WATCHED_FILE = os.path.join(BASE, "data", "watched.txt")
ANALYZED_FILE = os.path.join(BASE, "data", "analyzed_films.json")

# === TUR PROFILI (OWL zevk agirligi) ===
TASTE_W = {
    "Philosophical": 10, "Psychological": 9, "Action": 9, "Drama": 8, "Fantasy": 8,
    "Comedy": 8, "Sci-Fi": 7, "Slice of Life": 7, "Thriller": 7, "Romance": 5,
    "Mecha": 6, "Horror": 6, "Mystery": 7, "Suspense": 7,
    "Adventure": 7, "Supernatural": 7, "Ecchi": 4, "Sports": 7, "Music": 7,
}

# === KAYNAK ESLESTIRME ===
SOURCE_MAP = {
    "ORIGINAL": "Original", "MANGA": "Manga", "LIGHT_NOVEL": "Light Novel",
    "NOVEL": "Novel", "VISUAL_NOVEL": "Visual Novel", "WEB_NOVEL": "Web Novel",
    "GAME": "Game",
}

# =====================================================================
# LOYALTY / SERIALIZE — JSON corruption'a dayaniklidir
# =====================================================================
def _safe_json_dumps(obj, path):
    """Atomik yazma: once tmp, sonra rename. corruption korumasi."""
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception as e:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise

def _safe_json_load(path, default=None):
    """Guvenli JSON okuma. Bozuk dosya icin default doner."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, OSError):
        return default if default is not None else {}

# =====================================================================
# DUPLICATE TEMIZLEME (Bug 2-3 duzeltmesi)
# =====================================================================
def _normalize_title(t):
    """Title'i normalize et: kucuk harf, trim, colour->color vb."""
    if not t:
        return ""
    t = t.lower().strip()
    # Yazim farkliliklarini düzelt
    t = t.replace("colour", "color")
    t = t.replace("grey", "gray")
    t = t.replace("favourite", "favorite")
    t = re.sub(r"\s+", " ", t)
    return t

def deduplicate_films():
    """
    FILMS listesindeki duplicate temizligi.
    build.py ve analyzed_films.json icin.
    Aynı film (normalize title ile) birden fazla kez eklenmisse ilki tutulur.
    """
    results = {"db_fixed": 0, "json_fixed": 0}

    # 1. DB duplicate temizligi (title_lower UNIQUE zaten engelliyor, ama emin olalim)
    db = get_db()
    dups = db.execute(
        "SELECT title_lower, COUNT(*) as c, GROUP_CONCAT(id, ',') as ids FROM films GROUP BY title_lower HAVING c > 1"
    ).fetchall()
    for row in dups:
        ids = row["ids"].split(",")
        # Ilki tut, geri kalanlari sil
        for dup_id in ids[1:]:
            db.execute("DELETE FROM films WHERE id = ?", (dup_id,))
            results["db_fixed"] += 1
    db.commit()

    # 2. Build.py FILMS listesi (inline kontrol)
    build_path = os.path.join(BASE, "build.py")
    if os.path.exists(build_path):
        try:
            with open(build_path, encoding="utf-8") as f:
                build_content = f.read()
            # FILMS listesini bul ve temizle
            films_match = re.search(r'FILMS\s*=\s*\[(.*?)\]', build_content, re.DOTALL)
            if films_match:
                films_text = films_match.group(1)
                titles = re.findall(r'"t"\s*:\s*"([^"]+)"', films_text)
                seen = set()
                new_films = []
                removed = 0
                for film_block in re.findall(r'\{[^{}]+\}', films_text):
                    t_match = re.search(r'"t"\s*:\s*"([^"]+)"', film_block)
                    if t_match:
                        nt = _normalize_title(t_match.group(1))
                        if nt not in seen:
                            seen.add(nt)
                            new_films.append(film_block)
                        else:
                            removed += 1
                if removed > 0:
                    new_films_text = ",\n    ".join(new_films)
                    new_content = build_content[:films_match.start(1)] + "\n    " + new_films_text + "\n" + build_content[films_match.end(1):]
                    with open(build_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    results["json_fixed"] += removed
        except Exception as e:
            print(f"⚠️ build.py duplicate temizligi basarisiz: {e}")

    # 3. analyzed_films.json duplicate temizligi
    if os.path.exists(ANALYZED_FILE):
        try:
            data = _safe_json_load(ANALYZED_FILE, [])
            if data:
                seen = {}
                clean = []
                for film in data:
                    # title vs t tutarsizligi cozumu (Bug 3)
                    t = film.get("t") or film.get("title", "")
                    nt = _normalize_title(t)
                    if nt and nt not in seen:
                        seen[nt] = True
                        # Standart: "t" anahtari kullan
                        film["t"] = t
                        if "title" in film:
                            del film["title"]
                        clean.append(film)
                    else:
                        results["json_fixed"] += 1
                if results["json_fixed"] > 0:
                    _safe_json_dumps(clean, ANALYZED_FILE)
        except Exception as e:
            print(f"⚠️ analyzed_films.json duplicate temizligi basarisiz: {e}")

    db.close()
    return results

# =====================================================================
# WATCHED MANAGEMENT
# =====================================================================
def load_watched_set():
    """
    watched.txt'den izlenen film setini yukle.
    Bug 5 duzeltmesi: encoding="utf-8", try/except
    """
    watched = set()
    try:
        if os.path.exists(WATCHED_FILE):
            with open(WATCHED_FILE, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        watched.add(line.lower())
    except (OSError, UnicodeDecodeError) as e:
        print(f"⚠️ watched.txt okuma hatasi: {e}")
    return watched

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
            watched_at TEXT DEFAULT '',
            media_type TEXT DEFAULT 'anime',
            status TEXT DEFAULT 'plan_to_watch',
            progress INTEGER DEFAULT 0,
            total_items INTEGER DEFAULT 0,
            mal_id INTEGER DEFAULT 0,
            anilist_id INTEGER DEFAULT 0,
            start_date TEXT DEFAULT '',
            end_date TEXT DEFAULT '',
            rewatch_count INTEGER DEFAULT 0,
            tags TEXT DEFAULT '[]'
        );
        CREATE INDEX IF NOT EXISTS idx_fo ON films(owl_score DESC);
        CREATE INDEX IF NOT EXISTS idx_fw ON films(is_watched);
        CREATE INDEX IF NOT EXISTS idx_ft ON films(title_lower);
        CREATE INDEX IF NOT EXISTS idx_fy ON films(year);
        CREATE INDEX IF NOT EXISTS idx_fs ON films(user_rating DESC);
        CREATE INDEX IF NOT EXISTS idx_ff ON films(format);
        CREATE INDEX IF NOT EXISTS idx_media_type ON films(media_type);
        CREATE INDEX IF NOT EXISTS idx_status ON films(status);
        CREATE INDEX IF NOT EXISTS idx_mal_id ON films(mal_id);
        CREATE TABLE IF NOT EXISTS watched(title_lower TEXT UNIQUE, title TEXT, watched_at TEXT, rating REAL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS watchlist(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            film_id INTEGER UNIQUE,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP,
            priority INTEGER DEFAULT 0,
            note TEXT DEFAULT '',
            FOREIGN KEY(film_id) REFERENCES films(id)
        );
        CREATE INDEX IF NOT EXISTS idx_wl ON watchlist(priority DESC, added_at);
    """)
    db.commit()
    return db

# === ANILIST API ===
ANILIST_URL = "https://graphql.anilist.co"

ANILIST_QUERY = """
query ($page: Int, $perPage: Int, $type: MediaType, $format: MediaFormat) {
  Page(page: $page, perPage: $perPage) {
    media(type: $type, format: $format, sort: SCORE_DESC, status: FINISHED) {
      id
      title { romaji english native }
      startDate { year }
      endDate { year }
      meanScore
      popularity
      genres
      studios { nodes { name } }
      source(version: 2)
      duration
      chapters
      volumes
      episodes
      description
      coverImage { medium large }
      format
      type
    }
  }
}
"""

def fetch_anilist(page=1, perPage=50, media_type="ANIME", fmt="MOVIE"):
    """AniList'ten veri ceker. media_type: ANIME/MANGA, fmt: MOVIE/TV/MANGA/NOVEL/LIGHT_NOVEL"""
    type_map = {"ANIME": "ANIME", "MANGA": "MANGA"}
    fmt_map = {
        "MOVIE": "MOVIE", "TV": "TV", "OVA": "OVA", "SPECIAL": "SPECIAL",
        "MANGA": "MANGA", "NOVEL": "NOVEL", "LIGHT_NOVEL": "LIGHT_NOVEL",
        "ONE_SHOT": "ONE_SHOT",
    }
    t = type_map.get(media_type, "ANIME")
    f = fmt_map.get(fmt, "MOVIE")
    variables = {"page": page, "perPage": perPage, "type": t, "format": f}
    data = json.dumps({"query": ANILIST_QUERY, "variables": variables}).encode()
    req = urllib.request.Request(ANILIST_URL, data=data, headers={
        "Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (Hermes-OWL/5.0)"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except:
        return None

def detect_media_type(format_str, episodes, chapters, volumes):
    """Format str'ye gore media_type belirle."""
    fmt = (format_str or "").upper()
    if fmt in ("MANGA", "ONE_SHOT"):
        return "manga"
    if fmt in ("NOVEL", "LIGHT_NOVEL"):
        return "light_novel"
    if chapters and chapters > 0 and not episodes:
        return "manga"
    return "anime"

def detect_source_for_type(source_str, media_type):
    """Media type'a gore kaynak belirle."""
    s = (source_str or "").upper().replace("-", "_")
    if media_type == "manga":
        return SOURCE_MAP.get(s, "Manga") if s in SOURCE_MAP else "Manga"
    if media_type == "light_novel":
        ln_map = {
            "LIGHT_NOVEL": "Light Novel", "WEB_NOVEL": "Web Novel",
            "NOVEL": "Novel", "VISUAL_NOVEL": "Visual Novel",
            "ORIGINAL": "Original", "MANGA": "Manga", "GAME": "Game",
        }
        return ln_map.get(s, "Light Novel")
    return SOURCE_MAP.get(s, "Other")

def import_anilist_data(pages=10, media_type="ANIME", fmt="MOVIE"):
    """
    AniList'ten veri ceker ve DB'ye yazar/ayarla.
    Fonksiyon API: build.py veya baska modullerden cagrilabilir.
    media_type: ANIME veya MANGA
    fmt: MOVIE, TV, OVA, SPECIAL, MANGA, NOVEL, LIGHT_NOVEL, ONE_SHOT
    """
    db = get_db()
    # Yeni kolonlar varsa ekle
    for col, typ in [
        ("synopsis","TEXT DEFAULT ''"),("duration","INTEGER DEFAULT 0"),
        ("episodes","INTEGER DEFAULT 1"),("cover_url","TEXT DEFAULT ''"),
        ("format","TEXT DEFAULT 'MOVIE'"),("media_type","TEXT DEFAULT 'anime'"),
        ("status","TEXT DEFAULT 'plan_to_watch'"),("progress","INTEGER DEFAULT 0"),
        ("total_items","INTEGER DEFAULT 0"),("mal_id","INTEGER DEFAULT 0"),
        ("anilist_id","INTEGER DEFAULT 0"),("start_date","TEXT DEFAULT ''"),
        ("end_date","TEXT DEFAULT ''"),("rewatch_count","INTEGER DEFAULT 0"),
        ("tags","TEXT DEFAULT '[]'"),
    ]:
        try: db.execute(f"ALTER TABLE films ADD COLUMN {col} {typ}")
        except: pass
    db.commit()

    added = updated = 0
    for page in range(1, pages + 1):
        result = fetch_anilist(page, media_type=media_type, fmt=fmt)
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
            src_raw = m.get("source", "")
            gj = json.dumps(genres)
            pop = m.get("popularity", 0)
            dur = m.get("duration", 0) or 0
            desc = (m.get("description") or "")[:600]
            cover = (m.get("coverImage") or {}).get("large") or (m.get("coverImage") or {}).get("medium", "")
            format_str = m.get("format", fmt)
            episodes = m.get("episodes", 0) or 0
            chapters = m.get("chapters", 0) or 0
            volumes = m.get("volumes", 0) or 0

            # Media type ve kaynak belirle
            mt = detect_media_type(format_str, episodes, chapters, volumes)
            src = detect_source_for_type(src_raw, mt)

            # toplam item sayisi
            total_items = episodes if mt == "anime" else chapters

            start_d = ""
            end_d = ""
            sd = m.get("startDate", {})
            ed = m.get("endDate", {})
            if sd and sd.get("year"):
                try:
                    start_d = f"{sd.get('year','')}-{int(sd.get('month',0)):02d}-{int(sd.get('day',0)):02d}"
                except: start_d = ""
            if ed and ed.get("year"):
                try:
                    end_d = f"{ed.get('year','')}-{int(ed.get('month',0)):02d}-{int(ed.get('day',0)):02d}"
                except: end_d = ""

            anilist_id = m.get("id", 0)

            gb = sum(TASTE_W.get(g, 5) for g in genres) / max(len(genres), 1) * 0.05
            yb = 0.15 if year >= 2020 else (0.08 if year >= 2010 else 0.03)
            pb = 0.1 if pop > 1000 else (0.05 if pop > 500 else 0)
            ow = min(round(score + gb + yb + pb, 1), 10.0)

            try:
                db.execute("""INSERT INTO films(title,title_lower,year,studio,mal_score,owl_score,
                    source,genres,popularity,duration,synopsis,cover_url,format,media_type,
                    total_items,anilist_id,start_date,end_date)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (title, tl, year, studio, score, ow, src, gj, pop, dur, desc, cover,
                     format_str, mt, total_items, anilist_id, start_d, end_d))
                added += 1
            except sqlite3.IntegrityError:
                db.execute("""UPDATE films SET mal_score=?,owl_score=?,genres=?,popularity=?,
                    duration=?,synopsis=?,cover_url=?,studio=?,source=?,format=?,media_type=?,
                    total_items=?,anilist_id=?,start_date=?,end_date=?
                    WHERE title_lower=?""",
                    (score, ow, gj, pop, dur, desc, cover, studio, src, format_str, mt,
                     total_items, anilist_id, start_d, end_d, tl))
                updated += 1
        print(f"Sayfa {page}: {len(items)} item")
    db.commit()
    total = db.execute("SELECT COUNT(*) FROM films").fetchone()[0]
    print(f"\nEklenen: {added}, Guncellenen: {updated}, Toplam: {total}")
    return added + updated

# === OMDB API - IMDB SKOR CEKME ===
OMDB_API_KEY = os.environ.get("OMDB_API_KEY", "")

def fetch_omdb_rating(title, year=None):
    """OMDb API'den IMDB skoru ceker. API key gerekli."""
    if not OMDB_API_KEY:
        return None
    try:
        q = urllib.parse.quote(title)
        url = f"http://www.omdbapi.com/?t={q}&apikey={OMDB_API_KEY}"
        if year:
            url += f"&y={year}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        if data.get("Response") == "True":
            imdb = data.get("imdbRating", "N/A")
            if imdb and imdb != "N/A":
                return float(imdb)
    except Exception:
        pass
    return None

def fetch_imdb_scores(limit=50, force=False):
    """
    IMDB skoru olmayan filmler icin OMDb API'den skor ceker.
    limit: kac film guncellenecek (rate limit korumasi)
    force: True ise mevcut skorlari da guncelle
    """
    if not OMDB_API_KEY:
        print("⚠️ OMDB_API_KEY ortam degiskeni ayarli degil.")
        print("   https://www.omdbapi.com/apikey.aspx adresinden ucretsiz key alin.")
        print("   export OMDB_API_KEY=your_key")
        return 0
    db = get_db()
    if force:
        missing = db.execute(
            "SELECT id, title, year FROM films WHERE imdb_score = 0 OR imdb_score IS NULL LIMIT ?",
            (limit,)
        ).fetchall()
    else:
        missing = db.execute(
            "SELECT id, title, year FROM films WHERE imdb_score = 0 OR imdb_score IS NULL LIMIT ?",
            (limit,)
        ).fetchall()
    updated = 0
    errors = 0
    for row in missing:
        try:
            score = fetch_omdb_rating(row["title"], row["year"])
            if score:
                db.execute("UPDATE films SET imdb_score=? WHERE id=?", (score, row["id"]))
                updated += 1
                print(f"  ✅ {row['title']} ({row['year']}) -> IMDB: {score}")
            else:
                errors += 1
                print(f"  ⚠️ {row['title']} ({row['year']}) -> bulunamadi")
            db.commit()
            import time
            time.sleep(0.5)  # Rate limit: ~2 req/sec for free tier
        except Exception as e:
            errors += 1
            print(f"  ❌ {row['title']}: {e}")
    total = db.execute("SELECT COUNT(*) FROM films WHERE imdb_score > 0").fetchone()[0]
    all_total = db.execute("SELECT COUNT(*) FROM films").fetchone()[0]
    pct = total / all_total * 100 if all_total else 0
    print(f"\nIMDB skoru: {total}/{all_total} (%{pct:.1f})")
    print(f"Guncellenen: {updated}, Hata: {errors}")
    db.close()
    return updated

# === EXPORT ===
def export_csv(output_path=None):
    """Tum filmlerin CSV ciktisini uretir."""
    db = get_db()
    rows = db.execute("""
        SELECT id, title, year, director, studio, mal_score, imdb_score, owl_score,
               source, genres, popularity, duration, format, is_watched, user_rating,
               user_note, synopsis, cover_url
        FROM films ORDER BY owl_score DESC
    """).fetchall()
    db.close()
    if not output_path:
        os.makedirs(os.path.join(BASE, "output"), exist_ok=True)
        output_path = os.path.join(BASE, "output", "films_export.csv")
    fieldnames = ["id","title","year","director","studio","mal_score","imdb_score",
                  "owl_score","source","genres","popularity","duration","format",
                  "is_watched","user_rating","user_note","synopsis","cover_url"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            d = dict(row)
            d["genres"] = ", ".join(json.loads(d["genres"])) if d.get("genres") and d["genres"] != "[]" else ""
            d["is_watched"] = "Evet" if d.get("is_watched") else "Hayir"
            writer.writerow(d)
    print(f"CSV export: {output_path} ({len(rows)} film)")
    return output_path

def export_watchlist_csv(output_path=None):
    """Watchlist'in CSV ciktisini uretir."""
    db = get_db()
    rows = db.execute("""
        SELECT f.id, f.title, f.year, f.owl_score, f.mal_score, f.imdb_score,
               f.studio, f.source, f.genres, w.priority, w.note, w.added_at
        FROM watchlist w JOIN films f ON f.id = w.film_id
        ORDER BY w.priority DESC, w.added_at DESC
    """).fetchall()
    db.close()
    if not output_path:
        os.makedirs(os.path.join(BASE, "output"), exist_ok=True)
        output_path = os.path.join(BASE, "output", "watchlist_export.csv")
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID","Title","Year","OWL","MAL","IMDB","Studio","Source","Genres","Priority","Note","Added"])
        for r in rows:
            genres = ", ".join(json.loads(r["genres"])) if r["genres"] and r["genres"] != "[]" else ""
            writer.writerow([r["id"], r["title"], r["year"], r["owl_score"], r["mal_score"],
                           r["imdb_score"], r["studio"], r["source"], genres, r["priority"], r["note"], r["added_at"]])
    print(f"Watchlist CSV: {output_path} ({len(rows)} film)")
    return output_path

# === FILM KARSILASTIRMA ===
# === EXPORT ===
def get_profile(db=None):
    """Kullanici profil verisini doner."""
    close_db = False
    if db is None:
        db = get_db()
        close_db = True
    try:
        total = db.execute("SELECT COUNT(*) FROM films").fetchone()[0]
        watched_count = db.execute("SELECT COUNT(*) FROM films WHERE is_watched=1").fetchone()[0]
        watchlist_count = db.execute("SELECT COUNT(*) FROM watchlist").fetchone()[0]
        rated_count = db.execute("SELECT COUNT(*) FROM films WHERE user_rating > 0").fetchone()[0]
        avg_user_rating = db.execute("SELECT AVG(user_rating) FROM films WHERE user_rating > 0").fetchone()[0]
        avg_owl_watched = db.execute("SELECT AVG(owl_score) FROM films WHERE is_watched=1").fetchone()[0]
        # Izleme gecmişi (son 20)
        history = db.execute("""
            SELECT f.id, f.title, f.year, f.owl_score, f.user_rating, f.watched_at, f.genres, f.cover_url
            FROM films f WHERE f.is_watched=1 ORDER BY f.watched_at DESC LIMIT 20
        """).fetchall()
        # Zevk profili
        taste_counts, taste_avg = get_taste_profile(db)
        # En cok izlenen turler
        genre_list = taste_counts.most_common(10)
        # En cok izlenen studyolar
        studio_counts = Counter()
        for row in db.execute("SELECT studio FROM films WHERE is_watched=1 AND studio NOT IN ('Unknown','')").fetchall():
            studio_counts[row["studio"]] += 1
        # En cok izlenen yillar
        year_counts = Counter()
        for row in db.execute("SELECT year FROM films WHERE is_watched=1 AND year > 0").fetchall():
            year_counts[(row["year"] // 10) * 10] += 1
        # Kaynak dagilimi
        source_counts = Counter()
        for row in db.execute("SELECT source FROM films WHERE is_watched=1").fetchall():
            source_counts[row["source"]] += 1
        return {
            "total": total,
            "watched_count": watched_count,
            "watchlist_count": watchlist_count,
            "rated_count": rated_count,
            "avg_user_rating": round(avg_user_rating or 0, 1),
            "avg_owl_watched": round(avg_owl_watched or 0, 1),
            "history": [dict(r) for r in history],
            "taste_profile": dict(genre_list),
            "taste_avg": taste_avg,
            "top_studios": dict(studio_counts.most_common(5)),
            "top_years": dict(sorted(year_counts.items())),
            "top_sources": dict(source_counts.most_common(5)),
            "completion_pct": round(watched_count / total * 100, 1) if total else 0,
        }
    finally:
        if close_db:
            db.close()

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
    t = row["title"]
    print(f"✅ '{t}' izlendi (puan: {rating}). Toplam izlenen: {n}")
    return True

def rate_film(film_id, rating):
    db = get_db()
    row = db.execute("SELECT title FROM films WHERE id=?", (film_id,)).fetchone()
    if not row:
        print(f"❌ Film bulunamadi: id={film_id}")
        return False
    db.execute("UPDATE films SET user_rating=? WHERE id=?", (rating, film_id))
    db.commit()
    t = row["title"]
    print(f"✅ '{t}' puanlandi: {rating}/10")
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

# === WATCHLIST ===
def add_to_watchlist(film_id, priority=0, note=""):
    db = get_db()
    row = db.execute("SELECT title FROM films WHERE id=?", (film_id,)).fetchone()
    if not row:
        print(f"❌ Film bulunamadi: id={film_id}")
        return False
    t = row["title"]
    db.execute("INSERT OR REPLACE INTO watchlist(film_id,priority,note,added_at) VALUES(?,?,?,?)",
               (film_id, priority, note, datetime.now().isoformat()))
    db.commit()
    print(f"✅ '{t}' watchlist'e eklemdi (oncelik: {priority})")
    return True

def remove_from_watchlist(film_id):
    db = get_db()
    row = db.execute("SELECT f.title FROM films f JOIN watchlist w ON w.film_id=f.id WHERE w.film_id=?", (film_id,)).fetchone()
    db.execute("DELETE FROM watchlist WHERE film_id=?", (film_id,))
    db.commit()
    if row:
        print(f"✅ '{row['title']}' watchlist'ten cikarildi")
    else:
        print(f"✅ Film #{film_id} watchlist'ten cikarildi")
    return True

def list_watchlist(db=None, limit=50):
    close_db = False
    if db is None:
        db = get_db()
        close_db = True
    try:
        rows = db.execute("""
            SELECT f.id, f.title, f.year, f.owl_score, f.genres, f.studio, f.cover_url,
                   w.priority, w.note, w.added_at
            FROM watchlist w JOIN films f ON f.id = w.film_id
            ORDER BY w.priority DESC, w.added_at DESC LIMIT ?
        """, (limit,)).fetchall()
        return rows
    finally:
        if close_db:
            db.close()
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
    avg_scores = {}
    for g in genre_counts:
        avg_scores[g] = genre_scores[g] / genre_counts[g]
    return genre_counts, avg_scores

def get_taste_weights(db):
    counts, avg_scores = get_taste_profile(db)
    if not counts:
        return dict(TASTE_W)
    weights = dict(TASTE_W)
    total = sum(counts.values())
    for genre, count in counts.items():
        ratio = count / total
        if ratio > 0.1:
            weights[genre] = weights.get(genre, 5) + 2
        elif ratio > 0.05:
            weights[genre] = weights.get(genre, 5) + 1
    return weights

# === ONERI ALGORITMASI v5.0 ===
def recommend(db=None, category=None, genre=None, studio=None, source=None,
              year_from=0, year_to=2030, min_score=0, max_score=10,
              format_type=None, media_type=None, status=None,
              unwatched_only=True, limit=20, smart=True):
    """
    v5.1 Oneri algoritmasi:
    1. Filtreler (tur/yil/kaynak/format/media_type/status/puan)
    2. OWL skoru (AniList + zevk + yil + popularity)
    3. Content-based zevk profili bonusu
    4. Cesitlilik filtresi (her turden max 3)
    5. Dengeli popularite

    media_type: 'anime', 'manga', 'light_novel' (None = tumu)
    status: 'watching', 'completed', 'plan_to_watch', 'dropped', 'on_hold' (None = tumu)
    """
    close_db = False
    if db is None:
        db = get_db()
        close_db = True

    try:
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
        if genre:
            conditions.append("genres LIKE ?")
            params.append(f"%{genre}%")
        if category and not genre:
            conditions.append("genres LIKE ?")
            params.append(f"%{category}%")
        if media_type:
            conditions.append("media_type=?")
            params.append(media_type)
        if status:
            conditions.append("status=?")
            params.append(status)

        where = " AND ".join(conditions)
        q = f"SELECT * FROM films WHERE {where} ORDER BY owl_score DESC LIMIT ?"
        params.append(limit * 4)

        rows = db.execute(q, params).fetchall()
        if not rows:
            return []

        taste_weights = get_taste_weights(db) if smart else TASTE_W

        # Puanla
        scored = []
        for row in rows:
            base = row["owl_score"]

            genres = json.loads(row["genres"]) if row["genres"] and row["genres"] != "[]" else []
            if genres:
                taste_bonus = sum(taste_weights.get(g, 5) for g in genres) / len(genres) * 0.12
            else:
                taste_bonus = 0

            if row["user_rating"] > 0:
                user_bonus = (row["user_rating"] - 5) * 0.05
            else:
                user_bonus = 0

            year = row["year"] or 2010
            if year >= 2023:
                recency = 0.1
            elif year >= 2018:
                recency = 0.05
            else:
                recency = 0

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

        # Cesitlilik filtresi - her turden max 10
        genre_count = Counter()
        diverse = []
        for score, row in scored:
            genres = json.loads(row["genres"]) if row["genres"] and row["genres"] != "[]" else []
            main = genres[0] if genres else "Other"
            if genre_count[main] < 10:
                diverse.append((score, row))
                genre_count[main] += 1
            if len(diverse) >= limit:
                break

        return diverse
    finally:
        if close_db:
            db.close()

# === FILM DETAY ===
def get_detail(db, film_id):
    row = db.execute("SELECT * FROM films WHERE id=?", (film_id,)).fetchone()
    if not row:
        return None
    return dict(row)

# === ARAMA ===
def search_film(db, query, limit=20):
    q = f"%{query}%"
    return db.execute(
        """SELECT id,title,year,owl_score,studio,genres,cover_url 
           FROM films 
           WHERE title_lower LIKE ? 
              OR studio LIKE ? 
              OR director LIKE ? 
              OR source LIKE ?
              OR synopsis LIKE ?
           ORDER BY owl_score DESC LIMIT ?""",
        (q, q, q, q, q, limit)).fetchall()

# === ISTATISTIKLER ===
def get_stats(db=None):
    close_db = False
    if db is None:
        db = get_db()
        close_db = True
    try:
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
    finally:
        if close_db:
            db.close()

# === TXT RAPOR (Bug 1 duzeltmesi: f degiskeni degistirildi) ===
def gen_report(db=None):
    close_db = False
    if db is None:
        db = get_db()
        close_db = True
    try:
        os.makedirs(TXT_DIR, exist_ok=True)
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        films = recommend(db, limit=500)
        with open(f"{TXT_DIR}/01_ana_liste.txt", "w", encoding="utf-8") as f:
            f.write(f"OWL ANIME & FILM ONERI LISTESI v5.0\nTarih: {now}\nToplam: {len(films)} oneri\n{'='*80}\n\n")
            for i, (score, row) in enumerate(films, 1):
                genres = json.loads(row["genres"]) if row["genres"] and row["genres"] != "[]" else []
                f.write(f"#{i:04d} | OWL:{score:.1f} | {row['title']} ({row['year']}) | {row['studio']} | {row['source']} | {', '.join(genres[:3])}\n")

        stats = get_stats(db)
        with open(f"{TXT_DIR}/02_stats.txt", "w", encoding="utf-8") as f:
            f.write(f"OWL ANIME & FILM ONERI SISTEMI v5.0 - ISTATISTIKLER\n{'='*80}\n\n")
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

        # Bug 1 duzeltmesi: istatistik.txt icin ayri dosya, f caprazi yok
        with open(f"{TXT_DIR}/03_analiz.txt", "w", encoding="utf-8") as f:
            f.write(f"OWL ANIME & FILM ANALIZ RAPORU v5.0\nTarih: {now}\n{'='*80}\n\n")
            f.write(f"En yuksek puanli 20 film:\n")
            top = db.execute("SELECT title, year, owl_score, studio FROM films ORDER BY owl_score DESC LIMIT 20").fetchall()
            # Bug 1: 'film' degiskeni kullanildi, 'f' dosya handle ile caprazmiyor
            for i, film in enumerate(top, 1):
                f.write(f"  {i:2d}. {film['title']} ({film['year']}) OWL:{film['owl_score']:.1f} - {film['studio']}\n")

            f.write(f"\nEn iyi 10 studio:\n")
            for i, (s, c) in enumerate(stats["studios"][:10], 1):
                f.write(f"  {i:2d}. {s}: {c} film\n")

            f.write(f"\nTur dagilimi:\n")
            for g, c in stats["genre_ranking"][:15]:
                bar = "█" * min(c // 5, 40)
                f.write(f"  {g:20s}: {bar} ({c})\n")

        return len(films)
    finally:
        if close_db:
            db.close()

# === WEB ARAYUZ v5.0 ===
def start_web_server(port=8080):
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import urllib.parse, html as htmlmod

    class Handler(BaseHTTPRequestHandler):
        def get_db(self):
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
            elif path == "/watchlist":
                self._serve_watchlist(params)
            elif path == "/profile":
                self._serve_profile()
            elif path == "/api/recommend":
                self._api_recommend(params)
            elif path == "/api/search":
                self._api_search(params)
            elif path == "/api/stats":
                self._api_stats()
            elif path == "/api/dump":
                self._api_dump_all()
            elif path == "/api/watchlist":
                self._api_watchlist(params)
            elif path == "/api/profile":
                self._api_profile()
            elif path == "/api/export/csv":
                self._api_export_csv()
            elif path == "/api/export/watchlist":
                self._api_export_watchlist()
            else:
                self.send_response(404)
                self.end_headers()

        def _serve_index(self, params):
            db = self.get_db()
            limit = min(int(params.get("limit", [50])[0]), 100)
            genre_f = params.get("genre", [None])[0]
            source_f = params.get("source", [None])[0]
            studio_f = params.get("studio", [None])[0]
            yf = int(params.get("year_from", [0])[0])
            yt = int(params.get("year_to", [2030])[0])
            ms = float(params.get("min_score", [0])[0])
            search_q = params.get("q", [None])[0]
            media_f = params.get("media_type", [None])[0]

            if search_q:
                films = search_film(db, search_q, limit)
                scored = [(r["owl_score"], r) for r in films]
                scored.sort(key=lambda x: x[0], reverse=True)
            else:
                scored = recommend(db, genre=genre_f, source=source_f, studio=studio_f,
                                   year_from=yf, year_to=yt, min_score=ms,
                                   media_type=media_f, limit=limit)
            stats = get_stats(db)
            # Type dagilimi (db.close() oncesi)
            type_counts = db.execute("SELECT media_type, COUNT(*) FROM films GROUP BY media_type ORDER BY COUNT(*) DESC").fetchall()
            db.close()

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

                # Media type badge
                mt = row["media_type"] or "anime"
                mt_icons = {"anime":"🎬","manga":"📖","light_novel":"📚","web_novel":"🌐"}
                mt_labels = {"anime":"Anime","manga":"Manga","light_novel":"LN","web_novel":"WN"}
                mt_icon = mt_icons.get(mt, "🎬")
                mt_label = mt_labels.get(mt, mt)
                mt_badge = f'<span class="badge" style="background:rgba(236,72,153,0.12);color:var(--pink);border-color:rgba(236,72,153,0.2)">{mt_icon} {mt_label}</span>'

                # Progress bar (manga/LN icin)
                progress_html = ""
                total_items = row["total_items"] or 0 or 0
                progress = row["progress"] or 0 or 0
                if total_items > 0 and mt != "anime":
                    pct = min(int(progress / total_items * 100), 100)
                    item_label = "ch" if mt == "manga" else "vol"
                    progress_html = f'<div class="progress-bar"><div class="progress-fill" style="width:{pct}%"></div></div><span class="progress-text">{progress}/{total_items} {item_label}</span>'
                elif row["episodes"] and mt == "anime" and row["format"] == "TV":
                    eps = row["episodes"] or 0
                    progress_html = f'<span class="progress-text">{progress}/{eps} ep</span>'

                film_html += f"""
                <a href="/film?id={row['id']}" class="film-card {watched_class}">
                    {cover_html}
                    <div class="film-info">
                        <div class="film-title">#{i} {htmlmod.escape(row["title"])}</div>
                        <div class="film-meta">{row["year"]} · {htmlmod.escape(row["studio"])} · {row["source"]}{user_r}</div>
                        <div class="film-score">{score}</div>
                        <div class="film-badges">{mt_badge}{badges}</div>
                        {progress_html}
                    </div>
                </a>"""

            type_stats = " · ".join(f"{t[0]}: {t[1]}" for t in type_counts)

            # Type toggle butonlari
            type_btns = ""
            for mt_val, mt_icon, mt_name in [(None,"🌐","Tümü"),("anime","🎬","Anime"),("manga","📖","Manga"),("light_novel","📚","LN")]:
                active = " style=\"background:linear-gradient(135deg,var(--purple),var(--pink));color:#fff\"" if mt_val == media_f else ""
                href = f"/?media_type={mt_val}" if mt_val else "/"
                type_btns += f'<a href="{href}" class="btn btn-sm"{active}>{mt_icon} {mt_name}</a>'

            sq = htmlmod.escape(search_q or "")
            yf_val = yf if yf else ""
            yt_val = yt if yt != 2030 else ""
            ms_val = ms if ms else ""

            content = f"""
            <div class="stats-bar">
                <span>📊 {stats["total"]} item</span>
                <span>✅ {stats["watched"]} izlenen</span>
                <span>⭐ Ort: {stats["avg_score"]:.1f}</span>
                <span>{type_stats}</span>
            </div>
            <div class="type-toggle">
                {type_btns}
            </div>
            <div class="filters">
                <form method="GET" action="/">
                    <div class="filter-row">
                        <input type="text" name="q" placeholder="🔍 Ara..." value="{sq}" class="search-input">
                        <select name="genre"><option value="">Tum Turler</option>{genre_opts}</select>
                        <select name="source"><option value="">Tum Kaynaklar</option>{source_opts}</select>
                        <input type="number" name="year_from" placeholder="Yil baslangic" value="{yf_val}" class="year-input">
                        <input type="number" name="year_to" placeholder="Yil bitis" value="{yt_val}" class="year-input">
                        <input type="number" name="min_score" placeholder="Min OWL" value="{ms_val}" step="0.5" class="score-input">
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
                db.close()
                return

            genres = json.loads(film["genres"]) if film["genres"] and film["genres"] != "[]" else []
            badges = "".join(f'<span class="badge">{g}</span>' for g in genres)
            cover = film["cover_url"] or ""
            cover_html = f'<img src="{cover}" class="detail-cover" onerror="this.parentElement.innerHTML=\'<div class=detail-cover-placeholder>🎬</div>\'">' if cover else '<div class="detail-cover-placeholder">🎬</div>'
            synopsis = htmlmod.escape(film["synopsis"] or "Ozet yok.")
            watched = "✅ Izlenmis" if film["is_watched"] else "📋 Bekliyor"
            user_r = f"⭐ Kullanıcı: {film['user_rating']}/10" if film["user_rating"] > 0 else "Kullanıcı puani yok"
            note = f'<div class="note">📝 {htmlmod.escape(film["user_note"])}</div>' if film["user_note"] else ""
            duration = f"{film['duration']} dk" if film["duration"] > 0 else "?"
            year = film["year"] or "?"

            imdb_html = f'<span class="score-box imdb">IMDB: {film["imdb_score"]:.1f}</span>' if film["imdb_score"] > 0 else ""
            watched_btn = "✅ İzlendi" if film["is_watched"] else "📋 İzlendi İşaretle"
            wl_btn = "📋 Watchlist'ten Çıkar" if db.execute("SELECT 1 FROM watchlist WHERE film_id=?", (film_id,)).fetchone() else "➕ Watchlist'e Ekle"
            wl_action = "remove" if "Çıkar" in wl_btn else "add"

            content = f"""
            <a href="/" class="back-link">← Geri</a>
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
                            {imdb_html}
                            {f'<span class="score-box user">{user_r}</span>' if film["user_rating"] > 0 else ""}
                        </div>
                        <div class="detail-badges">{badges}</div>
                        <div class="detail-actions">
                            <a href="/watchlist?action={wl_action}&id={film_id}" class="btn btn-sm btn-wl">{wl_btn}</a>
                            <a href="/api/watchlist?action=add&id={film_id}" class="btn btn-sm btn-watched" onclick="markWatched({film_id})">{watched_btn}</a>
                        </div>
                    </div>
                </div>
                <div class="detail-synopsis">
                    <h3>Özet</h3>
                    <p>{synopsis}</p>
                </div>
                {note}
            </div>
            """
            self._send_html(film["title"], content, "detail")
            db.close()

        def _api_recommend(self, params):
            db = self.get_db()
            limit = min(int(params.get("limit", [50])[0]), 100)
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
            limit = min(int(params.get("limit", [50])[0]), 100)
            if not q:
                self._send_json([])
                db.close()
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

        def _api_watchlist(self, params):
            db = self.get_db()
            action = params.get("action", ["list"])[0]
            if action == "list":
                rows = list_watchlist(db)
                result = []
                for r in rows:
                    result.append({
                        "id": r["id"], "title": r["title"], "year": r["year"],
                        "score": r["owl_score"], "genres": json.loads(r["genres"]) if r["genres"] and r["genres"] != "[]" else [],
                        "studio": r["studio"], "cover_url": r["cover_url"],
                        "priority": r["priority"], "note": r["note"], "added_at": r["added_at"],
                    })
                db.close()
                self._send_json(result)
            elif action == "add":
                film_id = int(params.get("id", [0])[0])
                priority = int(params.get("priority", [0])[0])
                note = params.get("note", [""])[0]
                row = db.execute("SELECT title FROM films WHERE id=?", (film_id,)).fetchone()
                if row:
                    db.execute("INSERT OR REPLACE INTO watchlist(film_id,priority,note,added_at) VALUES(?,?,?,?)",
                               (film_id, priority, note, datetime.now().isoformat()))
                    db.commit()
                    t = row["title"]
                    db.close()
                    self._send_json({"ok": True, "message": f"'{t}' watchlist'e eklendi"})
                else:
                    db.close()
                    self._send_json({"ok": False, "error": "Film bulunamadi"})
            elif action == "remove":
                film_id = int(params.get("id", [0])[0])
                db.execute("DELETE FROM watchlist WHERE film_id=?", (film_id,))
                db.commit()
                db.close()
                self._send_json({"ok": True, "message": f"Film #{film_id} cikarildi"})
            else:
                db.close()
                self.send_response(400)
                self.end_headers()

        # === YENI API: PROFIL ===
        def _api_profile(self):
            db = self.get_db()
            profile = get_profile(db)
            db.close()
            self._send_json(profile)

        def _api_export_csv(self):
            path = export_csv()
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", "attachment; filename=films_export.csv")
            self.end_headers()
            with open(path, "rb") as f:
                self.wfile.write(f.read())

        def _api_export_watchlist(self):
            path = export_watchlist_csv()
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", "attachment; filename=watchlist_export.csv")
            self.end_headers()
            with open(path, "rb") as f:
                self.wfile.write(f.read())

        # === YENI SAYFA: WATCHLIST ===
        def _serve_watchlist(self, params):
            db = self.get_db()
            action = params.get("action", [None])[0]
            if action == "add":
                fid = int(params.get("id", [0])[0])
                pri = int(params.get("priority", [0])[0])
                note = params.get("note", [""])[0]
                row = db.execute("SELECT title FROM films WHERE id=?", (fid,)).fetchone()
                if row:
                    db.execute("INSERT OR REPLACE INTO watchlist(film_id,priority,note,added_at) VALUES(?,?,?,?)",
                              (fid, pri, note, datetime.now().isoformat()))
                    db.commit()
            elif action == "remove":
                fid = int(params.get("id", [0])[0])
                db.execute("DELETE FROM watchlist WHERE film_id=?", (fid,))
                db.commit()

            rows = list_watchlist(db)
            stats = get_stats(db)
            profile = get_profile(db)
            db.close()

            watchlist_html = ""
            priority_labels = {0: "⚪ Normal", 1: "🟡 Düşük", 2: "🟠 Yüksek", 3: "🔴 Acil"}
            for i, r in enumerate(rows, 1):
                genres = json.loads(r["genres"]) if r["genres"] and r["genres"] != "[]" else []
                badges = "".join(f'<span class="badge">{g}</span>' for g in genres[:4])
                cover = r["cover_url"] or ""
                cover_html = f'<img src="{cover}" class="cover" loading="lazy" onerror="this.style.display=\'none\'">' if cover else '<div class="cover placeholder">🎬</div>'
                pri_label = priority_labels.get(r["priority"], "⚪")
                note_html = f'<div class="wl-note">📝 {htmlmod.escape(r["note"])}</div>' if r["note"] else ""
                watchlist_html += f"""
                <div class="wl-card">
                    <a href="/film?id={r['id']}" class="wl-main">
                        {cover_html}
                        <div class="wl-info">
                            <div class="wl-title">#{i} {htmlmod.escape(r["title"])}</div>
                            <div class="wl-meta">{r["year"]} · {htmlmod.escape(r["studio"])} · OWL: {r["owl_score"]}</div>
                            <div class="wl-badges">{badges}</div>
                            <div class="wl-priority">{pri_label}</div>
                            {note_html}
                        </div>
                    </a>
                    <a href="/watchlist?action=remove&id={r['id']}" class="wl-remove" title="Çıkart">✕</a>
                </div>"""

            if not rows:
                watchlist_html = '<div class="empty-state">📋 Watchlist boş. Filmlere giderek "Watchlist\'e Ekle" butonunu kullanabilirsin.</div>'

            content = f"""
            <a href="/" class="back-link">← Ana Sayfa</a>
            <h2>📋 Watchlist</h2>
            <div class="profile-stats">
                <span>📋 {profile['watchlist_count']} film</span>
                <span>✅ {profile['watched_count']} izlenen</span>
                <span>🎯 %{profile['completion_pct']} tamamlandı</span>
            </div>
            <div class="wl-grid">{watchlist_html}</div>
            """
            self._send_html("Watchlist", content, "watchlist")

        # === YENI SAYFA: PROFIL ===
        def _serve_profile(self):
            db = self.get_db()
            profile = get_profile(db)
            db.close()

            # Zevk profili grafiği (basit bar chart)
            taste_bars = ""
            max_taste = max(profile["taste_profile"].values()) if profile["taste_profile"] else 1
            for genre, count in sorted(profile["taste_profile"].items(), key=lambda x: x[1], reverse=True)[:10]:
                pct = count / max_taste * 100
                taste_bars += f"""
                <div class="bar-row">
                    <span class="bar-label">{genre}</span>
                    <div class="bar-track"><div class="bar-fill" style="width:{pct}%"></div></div>
                    <span class="bar-val">{count}</span>
                </div>"""

            # İzleme geçmişi
            history_html = ""
            for h in profile["history"]:
                genres = json.loads(h["genres"]) if h.get("genres") and h["genres"] != "[]" else []
                cover = h.get("cover_url", "") or ""
                cover_html = f'<img src="{cover}" class="cover-sm" loading="lazy">' if cover else '<div class="cover-sm placeholder">🎬</div>'
                rating = f'⭐ {h["user_rating"]}' if h.get("user_rating") and h["user_rating"] > 0 else ""
                watched_at = h.get("watched_at", "")[:10] if h.get("watched_at") else ""
                history_html += f"""
                <a href="/film?id={h['id']}" class="history-card">
                    {cover_html}
                    <div>
                        <div class="history-title">{htmlmod.escape(h["title"])}</div>
                        <div class="history-meta">{h["year"]} · OWL: {h["owl_score"]} {rating}</div>
                        <div class="history-date">{watched_at}</div>
                    </div>
                </a>"""
            if not profile["history"]:
                history_html = '<div class="empty-state">Henüz film izlemedin. Filmleri görüntüleyip "İzlendi" diyebilirsin.</div>'

            # Studio/Year/Source dagilimi
            studio_html = "".join(f"<li>{s} <span>{c} film</span></li>" for s, c in profile.get("top_studios", {}).items())
            source_html = "".join(f"<li>{s} <span>{c}</span></li>" for s, c in profile.get("top_sources", {}).items())
            year_html = "".join(f"<li>{y}'lar <span>{c}</span></li>" for y, c in sorted(profile.get("top_years", {}).items()))

            content = f"""
            <a href="/" class="back-link">← Ana Sayfa</a>
            <h2>👤 Profil</h2>
            <div class="profile-stats">
                <div class="profile-stat"><span class="ps-num">{profile['watched_count']}</span><span class="ps-lbl">İzlenen</span></div>
                <div class="profile-stat"><span class="ps-num">{profile['watchlist_count']}</span><span class="ps-lbl">Watchlist</span></div>
                <div class="profile-stat"><span class="ps-num">{profile['rated_count']}</span><span class="ps-lbl">Puanlanan</span></div>
                <div class="profile-stat"><span class="ps-num">{profile['avg_user_rating']}</span><span class="ps-lbl">Ort. Puan</span></div>
                <div class="profile-stat"><span class="ps-num">%{profile['completion_pct']}</span><span class="ps-lbl">Tamamlanan</span></div>
            </div>

            <div class="profile-sections">
                <div class="prof-section">
                    <h3>🎯 Zevk Profili</h3>
                    <div class="bar-chart">{taste_bars if taste_bars else '<p class="muted">Yeterli veri yok.</p>'}</div>
                </div>

                <div class="prof-section">
                    <h3>🏢 En Çok İzlenen Stüdyolar</h3>
                    <ul class="prof-list">{studio_html if studio_html else '<li class="muted">Veri yok</li>'}</ul>
                </div>

                <div class="prof-section">
                    <h3>📚 Kaynak Dağılımı</h3>
                    <ul class="prof-list">{source_html if source_html else '<li class="muted">Veri yok</li>'}</ul>
                </div>

                <div class="prof-section">
                    <h3>📅 Yıl Dağılımı</h3>
                    <ul class="prof-list">{year_html if year_html else '<li class="muted">Veri yok</li>'}</ul>
                </div>
            </div>

            <h3>📜 İzleme Geçmişi (Son {len(profile['history'])})</h3>
            <div class="history-grid">{history_html}</div>
            """
            self._send_html("Profil", content, "profile")

        # === YENI SAYFA: KARSILASTIRMA ===
        def _send_html(self, title, content, page="index"):
            nav_html = ""
            for p, icon, label in [("index","🏠","Ana Sayfa"),("watchlist","📋","Watchlist"),("profile","👤","Profil")]:
                cls = " active" if page == p else ""
                nav_html += f'<a href="/{p}" class="bn-item{cls}"><span class="bn-icon">{icon}</span><span>{label}</span></a>'
            page_title = htmlmod.escape(title)
            full = _ECHO_HTML_TEMPLATE.format(page_title=page_title, content=content, nav_html=nav_html)
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(full.encode())

        def _send_json(self, data):
            self.send_response(200)
            self.send_header("Content-Type","application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

        def log_message(self, format, *args):
            pass

    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"🌐 Web server baslatildi: http://localhost:{port}")
    print(f"   Watchlist: http://localhost:{port}/watchlist")
    print(f"   Profil: http://localhost:{port}/profile")
    print(f"   Karsilastir: http://localhost:{port}/compare")
    server.serve_forever()

# === CLI ===
def interactive(db):
    print("\n  OWL ANIME & FILM ONERI SISTEMI v5.0")
    print(f"  {db.execute('SELECT COUNT(*) FROM films').fetchone()[0]} film yuklu")
    print("="*50)
    while True:
        print("\n[K]Oneri [T]Tur [G]Genre [Y]Yil [P]Puan [W]Izledi [R]Rapor [S]Ara [I]Stats [D]Detay [L]Watchlist [A]Add-WL [U]Web [V]Profil [Z]Karsilastir [E]Export [Q]Cikis")
        c = input("Secim: ").strip().lower()
        if c == "q":
            break
        elif c == "k":
            films = recommend(db, limit=15)
            for i, (s, f) in enumerate(films, 1):
                genres = json.loads(f["genres"]) if f["genres"] and f["genres"] != "[]" else []
                imdb_s = f" IMDB:{f['imdb_score']:.1f}" if f['imdb_score'] > 0 else ""
                print(f"  {i:2d}.[{s:.1f}] {f['title']} ({f['year']}) - {f['studio']} | {','.join(genres[:2])}{imdb_s}")
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
            imdb_c = db.execute("SELECT COUNT(*) FROM films WHERE imdb_score > 0").fetchone()[0]
            print(f"  Toplam:{stats['total']} Izlenen:{stats['watched']} Kalan:{stats['unwatched']} Ort:{stats['avg_score']:.1f}")
            print(f"  IMDB skoru:{imdb_c}/{stats['total']} (%{imdb_c/stats['total']*100:.1f})")
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
                    print(f"  OWL: {film['owl_score']} | MAL: {film['mal_score']:.1f} | IMDB: {film['imdb_score']:.1f}")
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
        elif c == "l":
            rows = list_watchlist(db)
            if not rows:
                print("  Watchlist bos.")
            else:
                for i, r in enumerate(rows, 1):
                    pri = "!!!" if r["priority"] >= 3 else ("!" if r["priority"] >= 1 else "")
                    print(f"  {i:2d}. [{r['owl_score']:.1f}] {r['title']} ({r['year']}) {pri}")
                    if r["note"]:
                        print(f"      📝 {r['note']}")
        elif c == "a":
            try:
                fid = int(input("Film ID: "))
                pri = int(input("Oncelik (0-3): ") or "0")
                note = input("Not: ").strip()
                add_to_watchlist(fid, pri, note)
            except:
                print("  Gecersiz giris.")
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
        elif c == "v":
            profile = get_profile(db)
            print(f"\n  PROFIL")
            print(f"  Izlenen: {profile['watched_count']}/{profile['total']} (%{profile['completion_pct']})")
            print(f"  Watchlist: {profile['watchlist_count']}")
            print(f"  Puanlanan: {profile['rated_count']}")
            print(f"  Ort. puan: {profile['avg_user_rating']}")
            if profile['taste_profile']:
                print("  Zevk:", ", ".join(f"{g}:{c}" for g, c in list(profile['taste_profile'].items())[:5]))
            if profile['history']:
                print("  Son izlenen:")
                for h in profile['history'][:5]:
                    r = f" ⭐{h['user_rating']}" if h.get('user_rating') and h['user_rating'] > 0 else ""
                    print(f"    {h['title']} ({h['year']}){r}")
        elif c == "z":
            ids_str = input("Film IDleri (virgulle): ").strip()
            try:
                ids = [int(x.strip()) for x in ids_str.split(",") if x.strip()]
                films = compare_films(ids)
                if films:
                    print(format_comparison(films))
                else:
                    print("  Film bulunamadi.")
            except:
                print("  Gecersiz giris.")
        elif c == "e":
            fmt = input("Format (csv/watchlist): ").strip().lower()
            if fmt == "csv":
                p = export_csv()
                print(f"  CSV: {p}")
            elif fmt == "watchlist":
                p = export_watchlist_csv()
                print(f"  Watchlist CSV: {p}")
            else:
                print("  Gecersiz format.")

# === ANA ===
def main():
    p = argparse.ArgumentParser(description="OWL Anime & Film Oneri v5.0")
    p.add_argument("--cli", action="store_true")
    p.add_argument("--recommend", type=int, default=0)
    p.add_argument("--category", type=str)
    p.add_argument("--genre", type=str)
    p.add_argument("--studio", type=str)
    p.add_argument("--source", type=str)
    p.add_argument("--year-from", type=int, default=0)
    p.add_argument("--year-to", type=int, default=2030)
    p.add_argument("--min-score", type=float, default=0)
    p.add_argument("--max-score", type=float, default=10)
    p.add_argument("--format", type=str)
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--watched", action="store_true")
    p.add_argument("--report", action="store_true")
    p.add_argument("--stats", action="store_true")
    p.add_argument("--search", type=str)
    p.add_argument("--watch", type=int)
    p.add_argument("--rate", type=float, default=0)
    p.add_argument("--note", type=str)
    p.add_argument("--detail", type=int)
    p.add_argument("--import-anilist", type=int, default=0)
    p.add_argument("--web", type=int, default=0)
    p.add_argument("--init", action="store_true")
    p.add_argument("--dedup", action="store_true", help="Duplicate film temizligi")
    p.add_argument("--add-watchlist", type=int, help="Watchlist'e film ekle (ID)")
    p.add_argument("--remove-watchlist", type=int, help="Watchlist'ten cikar (ID)")
    p.add_argument("--list-watchlist", action="store_true", help="Watchlist'i goster")
    p.add_argument("--watch-priority", type=int, default=0, help="Watchlist onceligi")
    p.add_argument("--watch-note", type=str, default="", help="Watchlist notu")
    # v5.0 yeni argumanlar
    p.add_argument("--fetch-imdb", action="store_true", help="OMDb ile IMDB skorlarini cek")
    p.add_argument("--fetch-limit", type=int, default=50, help="IMDB fetch limit")
    p.add_argument("--export", type=str, choices=["csv", "watchlist"], help="CSV export")
    p.add_argument("--profile", action="store_true", help="Kullanici profili")
    p.add_argument("--imdb-info", action="store_true", help="IMDB skoru istatistikleri")
    p.add_argument("--import-type", type=str, default="ANIME", help="AniList import tipi: ANIME/MANGA")
    p.add_argument("--import-fmt", type=str, default="MOVIE", help="AniList format: MOVIE/TV/MANGA/LIGHT_NOVEL/NOVEL")
    args = p.parse_args()

    if args.init:
        db = init_db()
        print("DB sifirlandi.")
        return

    if args.dedup:
        results = deduplicate_films()
        print(f"Duplicate temizligi: DB={results['db_fixed']}, JSON={results['json_fixed']}")
        return

    if args.add_watchlist:
        add_to_watchlist(args.add_watchlist, args.watch_priority, args.watch_note)
        return

    if args.remove_watchlist:
        remove_from_watchlist(args.remove_watchlist)
        return

    # v5.0: IMDB fetch
    if args.fetch_imdb:
        n = fetch_imdb_scores(limit=args.fetch_limit)
        return

    # v5.0: Export
    if args.export == "csv":
        path = export_csv()
        return
    if args.export == "watchlist":
        path = export_watchlist_csv()
        return

    # v5.0: IMDB info
    if args.imdb_info:
        db = get_db()
        total = db.execute("SELECT COUNT(*) FROM films").fetchone()[0]
        imdb_count = db.execute("SELECT COUNT(*) FROM films WHERE imdb_score > 0").fetchone()[0]
        imdb_pct = imdb_count / total * 100 if total else 0
        print(f"IMDB skoru olan: {imdb_count}/{total} (%{imdb_pct:.1f})")
        print(f"OMDB_API_KEY: {'Ayarli' if OMDB_API_KEY else 'Ayarli degil'}")
        if not OMDB_API_KEY:
            print("Key almak icin: https://www.omdbapi.com/apikey.aspx")
            print("Kullanim: export OMDB_API_KEY=your_key")
        db.close()
        return

    db = init_db()

    if args.list_watchlist:
        rows = list_watchlist(db)
        if not rows:
            print("Watchlist bos.")
        else:
            print(f"\n📋 WATCHLIST ({len(rows)} film)\n")
            for i, r in enumerate(rows, 1):
                genres = json.loads(r["genres"]) if r["genres"] and r["genres"] != "[]" else []
                pri = "🔴" if r["priority"] >= 3 else ("🟡" if r["priority"] >= 1 else "⚪")
                print(f"  {i:2d}. {pri} [{r['owl_score']:.1f}] {r['title']} ({r['year']}) - {r['studio']}")
                if r["note"]:
                    print(f"      📝 {r['note']}")
        return

    # v5.0: Profil
    if args.profile:
        profile = get_profile(db)
        print(f"\n👤 KULLANICI PROFILI\n")
        print(f"  Izlenen: {profile['watched_count']} / {profile['total']} (%{profile['completion_pct']})")
        print(f"  Watchlist: {profile['watchlist_count']}")
        print(f"  Puanlanan: {profile['rated_count']}")
        print(f"  Ort. kullanici puani: {profile['avg_user_rating']}")
        print(f"  Ort. OWL (izlenen): {profile['avg_owl_watched']}")
        if profile['taste_profile']:
            print(f"\n  Zevk profili:")
            for g, c in sorted(profile['taste_profile'].items(), key=lambda x: x[1], reverse=True)[:10]:
                avg = profile['taste_avg'].get(g, 0)
                print(f"    {g}: {c} film (ort: {avg:.1f})")
        if profile['top_studios']:
            print(f"\n  En cok izlenen studyolar:")
            for s, c in profile['top_studios'].items():
                print(f"    {s}: {c}")
        if profile['history']:
            print(f"\n  Son izlenen:")
            for h in profile['history'][:5]:
                rating = f" ⭐{h['user_rating']}" if h.get('user_rating') and h['user_rating'] > 0 else ""
                print(f"    {h['title']} ({h['year']}){rating}")
        return

    if args.import_anilist > 0:
        import_anilist_data(args.import_anilist, media_type=args.import_type, fmt=args.import_fmt)
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
        imdb_c = db.execute("SELECT COUNT(*) FROM films WHERE imdb_score > 0").fetchone()[0]
        print(f"IMDB skoru: {imdb_c}/{stats['total']} (%{imdb_c/stats['total']*100:.1f})")
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
        if args.note:
            note_film(args.watch, args.note)
        return

    if args.rate and not args.watch:
        print("Kullanim: --watch ID --rate PUAN")
        return

    if args.note and not args.watch:
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
            imdb_str = f" | IMDB:{f['imdb_score']:.1f}" if f['imdb_score'] > 0 else ""
            print(f"  {i:2d}.[{s:.1f}] {f['title']} ({f['year']}) - {f['studio']} | {','.join(genres[:3])}{imdb_str}")
        return

    if args.cli:
        interactive(db)
        return

if __name__ == "__main__":
    main()
