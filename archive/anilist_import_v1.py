#!/usr/bin/env python3
"""AniList import araci — oneri.py import_anilist_data() cagirir."""
import os
import sys

BASE = os.environ.get("ANIME_BASE", os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

def run(pages=10):
    """AniList'ten film ceker ve DB'ye yazar."""
    from oneri import init_db, import_anilist_data
    
    db = init_db()
    print(f"AniList'ten {pages} sayfa film cekiliyor...")
    result = import_anilist_data(pages)
    print(f"Toplam: {result} film isleme alindi.")
    db.close()
    return result

if __name__ == "__main__":
    pages = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    run(pages)
