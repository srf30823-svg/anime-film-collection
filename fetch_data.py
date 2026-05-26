#!/usr/bin/env python3
"""Echo Veri Genisletme - Kapsamlı"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oneri import init_db, import_anilist_data

configs = [
    ("ANIME", "MOVIE", 30, "Anime Movies"),
    ("ANIME", "TV", 50, "Anime TV Series"),
    ("ANIME", "OVA", 20, "Anime OVA"),
    ("ANIME", "SPECIAL", 10, "Anime Special"),
    ("ANIME", "ONA", 10, "Anime ONA"),
    ("MANGA", "MANGA", 50, "Manga"),
    ("MANGA", "ONE_SHOT", 15, "One Shot"),
    ("MANGA", "NOVEL", 20, "Novel"),
]

total = 0
for mt, fmt, pages, desc in configs:
    print(f"\n=== {desc} ({mt}/{fmt}) - {pages} sayfa ===")
    try:
        n = import_anilist_data(pages=pages, media_type=mt, fmt=fmt)
        total += n
        print(f"  -> {n} item")
    except Exception as e:
        print(f"  HATA: {e}")
        time.sleep(5)
    time.sleep(1)

from oneri import get_db
db = get_db()
t = db.execute("SELECT COUNT(*) FROM films").fetchone()[0]
types = db.execute("SELECT media_type, COUNT(*) FROM films GROUP BY media_type ORDER BY COUNT(*) DESC").fetchall()
print(f"\n{'='*50}")
print(f"TOPLAM: {t} item (bu islemde: {total})")
for mt, c in types:
    print(f"  {mt}: {c}")
db.close()
