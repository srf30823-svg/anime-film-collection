#!/usr/bin/env python3
"""
Echo Veri Genisletme Scripti
AniList'ten TV series, Manga, Light Novel ceker.
Kullanim: python3 fetch_data.py
"""
import sys, os, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oneri import init_db, import_anilist_data

def main():
    configs = [
        ("ANIME", "TV", 20, "Anime TV Series"),
        ("ANIME", "OVA", 5, "Anime OVA"),
        ("MANGA", "MANGA", 20, "Manga"),
        ("MANGA", "NOVEL", 10, "Light Novel"),
    ]
    
    total = 0
    for mt, fmt, pages, desc in configs:
        print(f"\n{'='*50}")
        print(f"  {desc} ({mt}/{fmt}) - {pages} sayfa")
        print(f"{'='*50}")
        try:
            n = import_anilist_data(pages=pages, media_type=mt, fmt=fmt)
            total += n
            print(f"  -> {n} item")
        except Exception as e:
            print(f"  HATA: {e}")
            time.sleep(3)
        time.sleep(1)
    
    from oneri import get_db
    db = get_db()
    t = db.execute("SELECT COUNT(*) FROM films").fetchone()[0]
    types = db.execute("SELECT media_type, COUNT(*) FROM films GROUP BY media_type ORDER BY COUNT(*) DESC").fetchall()
    print(f"\n{'='*50}")
    print(f"  TOPLAM: {t} item (bu islemde: {total})")
    for mt, c in types:
        print(f"    {mt}: {c}")
    db.close()

if __name__ == "__main__":
    main()
