#!/usr/bin/env python3
"""
Echo v5.3 - Synopsis Türkçe Çeviri Scripti
Tüm İngilizce synopsis'leri Türkçe'ye çevirir.
"""
import sqlite3, time, re, os, sys
from deep_translator import GoogleTranslator

DB_PATH = "/data/data/com.termux/files/home/anime-project/data/recommender.db"

def clean_html(text):
    """HTML tag'lerini temizle."""
    if not text:
        return ""
    text = re.sub(r'<br\s*/?>', ' ', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&#\d+;', '', text)
    text = re.sub(r'&[a-z]+;', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def translate_batch(texts, translator, batch_size=10):
    """Birden fazla metni toplu çevir."""
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_results = []
        for text in batch:
            try:
                if not text or len(text.strip()) < 3:
                    batch_results.append(text)
                    continue
                # Google Translate character limit ~5000
                if len(text) > 4500:
                    text = text[:4500]
                translated = translator.translate(text)
                if translated:
                    batch_results.append(translated.strip())
                else:
                    batch_results.append(text)
            except Exception as e:
                print(f"    Çeviri hatası: {e}")
                batch_results.append(text)
            time.sleep(0.1)  # Rate limit koruması
        results.extend(batch_results)
        print(f"  Batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size} tamamlandı")
    return results

def main():
    start_from = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # synopsis olan ama synopsis_tr OLMAYAN filmleri al
    c.execute("""
        SELECT id, title, synopsis FROM films 
        WHERE synopsis IS NOT NULL AND synopsis != ""
        AND (synopsis_tr IS NULL OR synopsis_tr = "")
        ORDER BY id
    """)
    all_films = c.fetchall()
    conn.close()
    
    # Kısa veya boş olanları ayıkla
    to_translate = []
    skipped = 0
    for film_id, title, syn in all_films:
        clean = clean_html(syn)
        if not clean or len(clean) < 10:
            skipped += 1
            continue
        to_translate.append((film_id, title, clean))
    
    print(f"Toplam film: {len(all_films)}")
    print(f"Çevrilecek: {len(to_translate)}")
    print(f"Başlangıç: {start_from}")
    print()
    
    # Çeviri yap
    translator = GoogleTranslator(source='en', target='tr')
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    translated_count = 0
    error_count = 0
    
    for i, (film_id, title, syn) in enumerate(to_translate):
        if i < start_from:
            continue
        
        try:
            # Çeviri
            if len(syn) > 4500:
                syn = syn[:4500]
            translated = translator.translate(syn)
            if translated and translated.strip():
                c.execute("UPDATE films SET synopsis_tr=? WHERE id=?", (translated.strip(), film_id))
                conn.commit()
                translated_count += 1
                if translated_count % 50 == 0:
                    print(f"  [{i+1}/{len(to_translate)}] {translated_count} çevrildi. Son: {title[:40]}")
            else:
                error_count += 1
        except Exception as e:
            error_count += 1
            if "429" in str(e) or "Too Many" in str(e):
                print(f"  RATE LIMIT! 30sn bekleniyor... ({i+1}/{len(to_translate)})")
                time.sleep(30)
                try:
                    translated = translator.translate(syn)
                    if translated:
                        c.execute("UPDATE films SET synopsis_tr=? WHERE id=?", (translated.strip(), film_id))
                        conn.commit()
                        translated_count += 1
                        error_count -= 1
                except:
                    pass
            elif error_count <= 10:
                print(f"  Hata: {title[:40]} - {e}")
        
        # Her 100 filmde bir durum raporu
        if (translated_count + error_count) % 100 == 0 and (translated_count + error_count) > 0:
            print(f"\n  >>> Durum: {translated_count} OK, {error_count} hata, {i+1}/{len(to_translate)}\n")
        
        # Rate limit: ~1 req/sec
        time.sleep(1.2)
    
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"Çeviri tamamlandı!")
    print(f"Çevrilen: {translated_count}")
    print(f"Hata: {error_count}")
    print(f"Başarı oranı: {translated_count/(translated_count+error_count)*100:.1f}%" if (translated_count+error_count) > 0 else "N/A")

if __name__ == "__main__":
    main()
