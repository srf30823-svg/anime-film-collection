# Echo - Anime & Film Öneri Sistemi

4778 anime/manga/light novel içeren, content-based filtreleme motoru ile akıllı öneri sistemi.

## Kurulum

```bash
# Depoyu klonla
git clone https://github.com/srf30823-svg/anime-film-collection.git
cd anime-film-collection

# Bağımlılıklar (Python 3.10+ ile built-in, ek paket gerekmez)
python3 --version

# DB başlatma (isteğe bağlı, ilk çalışmada otomatik oluşur)
python3 oneri.py --init
```

## Ortam Değişkenleri

| Değişken | Açıklama | Varsayılan |
|-----------|----------|------------|
| `ANIME_BASE` | Proje kök dizini | Dosyanın bulunduğu dizin |

```bash
# Özel dizin kullanmak için
export ANIME_BASE="/path/to/anime-project"
python3 oneri.py
```

## Kullanım

### CLI Komutları

```bash
# 10 öneri (varsayılan)
python3 oneri.py

# 20 öneri
python3 oneri.py --recommend 20

# Türe göre filtrele
python3 oneri.py --genre Psychological --recommend 10
python3 oneri.py --genre Action --min-score 8.5

# Kaynağa göre filtrele
python3 oneri.py --source Manga --recommend 10

# Studio, yıl, puan filtresi
python3 oneri.py --studio "Studio Ghibli"
python3 oneri.py --year-from 2020 --year-to 2025
python3 oneri.py --min-score 9.0

# Film ara
python3 oneri.py --search "your name"

# Film izle + puan ver
python3 oneri.py --watch FILM_ID --rate 9.5

# Film notu ekle
python3 oneri.py --watch FILM_ID --note "Muhtesem film"

# Film detay
python3 oneri.py --detail FILM_ID

# İstatistikler
python3 oneri.py --stats

# TXT rapor üret
python3 oneri.py --report

# AniList'ten import
python3 oneri.py --import-anilist 10

# Duplicate temizliği
python3 oneri.py --dedup

# İnteraktif CLI
python3 oneri.py --cli
```

### Web Arayüzü

```bash
python3 oneri.py --web 8080
# http://localhost:8080 adresinden erişin
```

### API Endpoints

| Endpoint | Açıklama | Parametreler |
|----------|----------|-------------|
| `GET /api/recommend` | Öneri listesi | `limit`, `genre`, `source`, `year_from`, `year_to`, `min_score`, `media_type` |
| `GET /api/search` | Film ara | `q`, `limit` |
| `GET /api/stats` | İstatistikler | - |
| `GET /api/dump` | Tüm filmler | - |
| `GET /api/watchlist` | Watchlist işlemleri | `action=list\|add\|remove\|watch\|unwatch\|rate`, `id`, `priority`, `note`, `rating` |
| `GET /api/profile` | Kullanıcı profili | - |
| `GET /api/export/csv` | CSV export | - |
| `GET /api/export/watchlist` | Watchlist CSV | - |
| `GET /film?id=ID` | Film detay (HTML) | `id` |

```
# Örnek API çağrıları:
curl "http://localhost:8080/api/recommend?limit=5&genre=Psychological"
curl "http://localhost:8080/api/search?q=ghibli&limit=10"
curl "http://localhost:8080/api/stats"
```

### Modül Olarak Kullanım

```python
from oneri import init_db, recommend, get_stats, mark_watched, rate_film
from oneri import import_anilist_data, search_film, get_detail, deduplicate_films

db = init_db()

# Öneri al
films = recommend(db, genre="Action", min_score=8.5, limit=10)
for score, film in films:
    print(f"[{score}] {film['title']} ({film['year']})")

# İstatistikler
stats = get_stats(db)
print(f"Toplam: {stats['total']}, Ortalama OWL: {stats['avg_score']}")

# İzle ve puanla
mark_watched(1, rating=9.5)

# Duplicate temizle
deduplicate_films()

db.close()
```

## Proje Yapısı

```
anime-project/
├── oneri.py              # Ana modül (CLI + Web + API)
├── build.py              # Film veri giriş aracı (v1)
├── anilist_import.py     # AniList API import aracı (v1)
├── data/
│   ├── recommender.db    # SQLite veritabanı (602 film)
│   ├── watched.txt       # İzlenen filmler listesi
│   └── analyzed_films.json # Analiz edilmiş film verileri
├── output/
│   └── txt/              # TXT raporları
├── .gitignore
└── README.md
```

## Algoritma

v5.2 öneri algoritması şu bileşenleri kullanır:

1. **OWL Skoru**: AniList puanı + tür bonusu + yıl/popularite farkı
2. **Zevk Profili**: İzlenen filmlerden çıkarılan tür ağırlıkları
3. **Recency Bonus**: 2024-2025 filmler için ek puan
4. **Popularite Dengesi**: Çok popüler/niş filmler arasında denge
5. **Stüdyo Kalitesi**: Bilinen stüdyolara bonus puan
6. **Çeşitlilik Filtresi**: Her türden dengeli dağılım
7. **Media Type Desteği**: Anime, Manga, Light Novel ayrı filtreleme

## Veri Kaynakları

- **AniList API**: Film bilgileri, türler, puanlar, studio bilgileri (4778+ item)
- **Manuel Giriş**: Klasik ve özel filmler
- **Format Desteği**: Movie, TV, OVA, Special, Manga, Novel, Light Novel, One Shot
