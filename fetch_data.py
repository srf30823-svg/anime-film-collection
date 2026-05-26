#!/usr/bin/env python3
"""
Echo Veri Genisletme Scripti
AniList'ten TV series, Manga, Light Novel, Web Novel ceker.
Rate limit: ~3 req/sec (guvenli)
"""
import sys, os, time

# Proje dizinini ekle
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from oneri import init_db, import_anilist_data, get_db

def bulk_import():
    """Tum medya turlerinden veri cek."""
    configs = [
        # (media_type, format, pages, aciklama)
        ("ANIME", "TV", 30, "Anime TV Series"),
        ("ANIME", "OVA", 10, "Anime OVA"),
        ("ANIME", "SPECIAL", 5, "Anime Special"),
        ("ANIME", "MOVIE", 20, "Anime Movies (ek)"),
        ("MANGA", "MANGA", 30, "Manga"),
        ("MANGA", "ONE_SHOT", 5, "One Shot Manga"),
        ("MANGA", "NOVEL", 10, "Light Novel"),
        ("MANGA", "LIGHT_NOVEL", 15, "Light Novel (ek)"),
    ]
    
    total_added = 0
    for media_type, fmt, pages, desc in configs:
        print(f"\n{'='*60}")
        print(f"  {desc} ({media_type}/{fmt}) - {pages} sayfa")
        print(f"{'='*60}")
        try:
            n = import_anilist_data(pages=pages, media_type=media_type, fmt=fmt)
            total_added += n
            print(f"  -> {n} item eklendi/guncellendi")
        except Exception as e:
            print(f"  HATA: {e}")
            time.sleep(5)
        
        time.sleep(2)  # Rate limit korumasi
    
    # Sonuc
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM films").fetchone()[0]
    types = db.execute("SELECT media_type, COUNT(*) FROM films GROUP BY media_type ORDER BY COUNT(*) DESC").fetchall()
    db.close()
    
    print(f"\n{'='*60}")
    print(f"  TOPLAM: {total} item")
    print(f"  Bu islemde eklenen/guncellenen: {total_added}")
    print(f"  Dagilim:")
    for t, c in types:
        print(f"    {t}: {c}")
    print(f"{'='*60}")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Echo veri genisletme")
    p.add_argument("--type", type=str, default="all", help="anime/manga/all")
    p.add_argument("--pages", type=int, default=10, help="Sayfa basina")
    args = p.parse_args()

    if args.type == "all":
        bulk_import()
    elif args.type == "anime":
        for fmt, pages in [("TV", 30), ("OVA", 10), ("MOVIE", 20)]:
            import_anilist_data(pages=pages, media_type="ANIME", fmt=fmt)
            time.sleep(2)
    elif args.type == "manga":
        for fmt, pages in [("MANGA", 30), ("NOVEL", 10), ("LIGHT_NOVEL", 15)]:
            import_anilist_data(pages=pages, media_type="MANGA", fmt=fmt)
            time.sleep(2)
