#!/usr/bin/env python3
"""
Echo Eksik Synopsis Doldurucu
Jikan API v4 ile eksik aciklamalari ceker ve DB'ye yazar.
Anime/Manga/LN icin calisir.
"""
import sqlite3, json, time, urllib.request, re, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "data", "recommender.db")

def clean_synopsis(text):
    """HTML temizle, referans temizle."""
    if not text:
        return ""
    # HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Jikan referans: [Written by ...], [MAL Rewrite], vs
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(Source:.*?\)', '', text)
    text = re.sub(r'\(Written by.*?\)', '', text)
    text = re.sub(r'\(MAL Rewrite.*?\)', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def jikan_search(title, media_type):
    """Jikan API'de ara, ilk sonucun id'sini doner."""
    tp = "anime" if media_type == "anime" else "manga"
    try:
        q = urllib.parse.quote(title)
        url = f"https://api.jikan.moe/v4/{tp}?q={q}&limit=1"
        req = urllib.request.Request(url, headers={"User-Agent": "Echo/5.2"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        if data.get("data"):
            return data["data"][0]["mal_id"]
    except Exception as e:
        print(f"  ARAMA HATA [{title}]: {e}")
    return None

def jikan_get_synopsis(mal_id, media_type):
    """Jikan API'den synopsis ceker."""
    tp = "anime" if media_type == "anime" else "manga"
    try:
        url = f"https://api.jikan.moe/v4/{tp}/{mal_id}/full"
        req = urllib.request.Request(url, headers={"User-Agent": "Echo/5.2"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        syn = data.get("data", {}).get("synopsis", "")
        return clean_synopsis(syn)
    except Exception as e:
        print(f"  GET HATA [mal_id={mal_id}]: {e}")
    return ""

def anilist_search_synopsis(title, media_type):
    """AniList GraphQL ile synopsis ceker (Jikan yedek)."""
    al_type = "ANIME" if media_type == "anime" else "MANGA"
    query = """
    query ($search: String, $type: MediaType) {
      Media(search: $search, type: $type) {
        id
        synopsis
      }
    }
    """
    variables = {"search": title, "type": al_type}
    try:
        body = json.dumps({"query": query, "variables": variables}).encode()
        req = urllib.request.Request(
            "https://graphql.anilist.co",
            data=body,
            headers={"Content-Type": "application/json", "User-Agent": "Echo/5.2"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        syn = data.get("data", {}).get("Media", {}).get("synopsis", "")
        return clean_synopsis(syn)
    except:
        return ""

def fetch_wikipedia_synopsis(title):
    """Wikipedia API ile ozet ceker (film icin)."""
    try:
        q = urllib.parse.quote(title)
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{q}"
        req = urllib.request.Request(url, headers={"User-Agent": "Echo/5.2"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        return data.get("extract", "")
    except:
        return ""

def main():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row

    # Eksik synopsis olan filmleri cek
    rows = db.execute(
        "SELECT id, title, media_type, mal_id, anilist_id FROM films "
        "WHERE (synopsis IS NULL OR synopsis = '') AND media_type IN ('anime','manga','light_novel') "
        "ORDER BY id"
    ).fetchall()

    total = len(rows)
    print(f"Eksik aciklama: {total} item")
    if total == 0:
        print("Tum aciklamalar mevcut!")
        return

    filled = 0
    failed = 0
    rate_limit = 0.4  # Jikan: ~3 req/sec

    for i, row in enumerate(rows, 1):
        fid = row["id"]
        title = row["title"]
        mt = row["media_type"] or "anime"
        mal_id = row["mal_id"]
        anilist_id = row["anilist_id"]

        print(f"[{i}/{total}] {title} ({mt})", end=" ... ")
        syn = ""

        # 1. Varsa Jikan mal_id ile direkt cek
        if mal_id and mal_id > 0:
            syn = jikan_get_synopsis(mal_id, mt)
            if syn:
                print(f"[Jikan mal_id={mal_id}] {len(syn)} char")

        # 2. Yoksa Jikan search ile bul
        if not syn:
            time.sleep(rate_limit)
            found_id = jikan_search(title, mt)
            if found_id:
                time.sleep(rate_limit)
                syn = jikan_get_synopsis(found_id, mt)
                if syn:
                    print(f"[Jikan search] {len(syn)} char")
                    # mal_id guncelle
                    db.execute("UPDATE films SET mal_id=? WHERE id=?", (found_id, fid))

        # 3. AniList yedek
        if not syn and anilist_id and anilist_id > 0:
            time.sleep(rate_limit)
            syn = anilist_search_synopsis(title, mt)
            if syn:
                print(f"[AniList] {len(syn)} char")

        # 4. Wikipedia yedek (ozellikle anime/film icin)
        if not syn:
            time.sleep(rate_limit)
            syn = fetch_wikipedia_synopsis(title)
            if syn:
                print(f"[Wiki] {len(syn)} char")

        if syn:
            db.execute("UPDATE films SET synopsis=? WHERE id=?", (syn, fid))
            db.commit()
            filled += 1
        else:
            failed += 1
            print("[BULUNAMADI]")

        time.sleep(rate_limit)

    print(f"\n=== SONUC ===")
    print(f"Doldurulan: {filled}/{total}")
    print(f"Basarisiz: {failed}/{total}")

    # Final kontrol
    remaining = db.execute(
        "SELECT COUNT(*) FROM films WHERE synopsis IS NULL OR synopsis=''"
    ).fetchone()[0]
    print(f"Kalan eksik: {remaining}")

    db.close()

if __name__ == "__main__":
    main()
