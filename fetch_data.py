#!/usr/bin/env python3
"""Echo Veri Genisletme - Kapsamlı import"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oneri import init_db, import_anilist_data

configs = [
    ("ANIME", "MOVIE", 50, "Anime Movies"),
    ("ANIME", "TV", 100, "Anime TV Series"),
    ("ANIME", "OVA", 30, "Anime OVA"),
    ("ANIME", "SPECIAL", 20, "Anime Special"),
    ("ANIME", "ONA", 20, "Anime ONA"),
    ("MANGA", "MANGA", 100, "Manga"),
    ("MANGA", "ONE_SHOT", 30, "One Shot"),
    ("MANGA", "NOVEL", 40, "Novel"),
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
