# Echo - Anime & Film Öneri Sistemi

4778 anime/manga/light novel + Türkçe synopsis, content-based filtreleme motoru ile akıllı öneri sistemi.

## v5.3 Yenilikler

- **Türkçe Synopsis**: 4764 filmin açıklaması Türkçe'ye çevrildi (Google Translate)
- **Günün Önerisi**: Her gün yeni bir film önerisi (tarihe göre sabit)
- **Rastgele Film**: İzlenmemiş filmler arası rastgele seçim
- **Detaylı İstatistikler**: `/api/stats/extended` — tür/yıl/stüdyo dağılımı
- **Anlık Arama**: Arama kutusunda 600ms debounce ile otomatik arama
- **Scroll to Top**: Sayfanın alta kaymasında ↑ butonu
- **Yedekleme**: `backup.py` ile SQLite + Memory yedekleme + GitHub push

## Kurulum

```bash
git clone https://github.com/srf30823-svg/anime-film-collection.git
cd anime-film-collection
python3 --version  # Python 3.10+
pip install deep_translator  # Çeviri için
python3 oneri.py --init
```

## Ortam Değişkenleri

| Değişken | Açıklama | Varsayılan |
|-----------|----------|------------|
| `ANIME_BASE` | Proje kök dizini | Dosyanın bulunduğu dizin |

## Kullanım

### CLI

```bash
python3 oneri.py                          # 10 öneri
python3 oneri.py --recommend 20           # 20 öneri
python3 oneri.py --genre Psychological    # Tür filtresi
python3 oneri.py --source Manga           # Kaynak filtresi
python3 oneri.py --studio "Studio Ghibli" # Studio filtresi
python3 oneri.py --search "your name"     # Arama
python3 oneri.py --watch FILM_ID --rate 9.5
python3 oneri.py --detail FILM_ID
python3 oneri.py --stats
python3 oneri.py --cli
```

### Web Arayüzü

```bash
python3 oneri.py --web 8080
# http://localhost:8080
```

### API Endpoints

| Endpoint | Açıklama | Parametreler |
|----------|----------|-------------|
| `GET /api/recommend` | Öneri listesi | `limit`, `genre`, `source`, `year_from`, `year_to`, `min_score`, `media_type` |
| `GET /api/search` | Film ara | `q`, `limit` |
| `GET /api/stats` | Temel istatistikler | - |
| `GET /api/stats/extended` | Detaylı istatistikler | - |
| `GET /api/daily` | Günün önerisi | - |
| `GET /api/dump` | Tüm filmler | - |
| `GET /api/watchlist` | Watchlist işlemleri | `action`, `id`, `priority`, `note`, `rating` |
| `GET /api/profile` | Kullanıcı profili | - |
| `GET /api/export/csv` | CSV export | - |
| `GET /random` | Rastgele film | `unwatched=1`, `media_type=` |
| `GET /daily` | Günün önerisi (redirect) | - |

### Modül Olarak

```python
from oneri import init_db, recommend, get_stats, mark_watched, rate_film
db = init_db()
films = recommend(db, genre="Action", limit=10)
db.close()
```

## Proje Yapısı

```
anime-project/
├── oneri.py              # Ana modül (CLI + Web + API)
├── fetch_data.py         # AniList import
├── fetch_synopsis.py     # Synopsis doldurma (Jikan/AniList/Wikipedia)
├── translate_synopsis.py # Türkçe çeviri
├── backup.py             # Yedekleme sistemi
├── data/
│   └── recommender.db    # SQLite (4778 item, ~5MB)
└── backups/
    └── *.gz              # Yedekler
```

## Veri

- **Toplam**: 4778 item
- **Anime**: 2634
- **Manga**: 1498
- **Light Novel**: 646
- **Türkçe synopsis**: 4764 (%99.8)
- **Kaynak**: AniList API + Jikan API + manuel
