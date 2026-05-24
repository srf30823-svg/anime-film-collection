# OWL - 2000 ADIMLI KAPSAMLI PROJE PLANI
# Lain Temali Anime GUI + Self-Improvement + Hafıza Sistemi
# Tarih: 2026-05-24
# Durum: Aktif

================================================================================
# FAZ 0: HAZIRLIK, TEMİZLUK VE ALTYAPI (Adım 1-50)
================================================================================

## A. Mevcut Durum Analizi (Adım 1-10)

Adım 1: Mevcut anime-film-collection repo durumunu kontrol et
  - git status, git log son 10 commit
  - Branch yapısını incele
  - Remote bağlantılarını kontrol et

Adım 2: build_v2.py scriptini analiz et - hataları tespit et
  - Syntax hatalarını kontrol et
  - Runtime hatalarını kontrol et
  - Veri akış hatalarını tespit et (year/categories/director key sorunları)
  - import/ export hatalarını kontrol et

Adım 3: output/txt/ dosyalarını kontrol et - bozuk dosyaları temizle
  - Her TXT dosyasının formatını doğrula
  - Encoding sorunlarını kontrol et (UTF-8)
  - Boş veya eksik dosyaları tespit et

Adım 4: data/analyzed_films.json'u kontrol et - veri bütünlüğünü doğrula
  - JSON syntax kontrolü
  - Her film için gerekli alanların varlığını kontrol et
  - year, categories, director, mal_score, imdb_score alanlarını doğrula

Adım 5: GitHub repo yapısını incele - gereksiz dosyaları tespit et
  - build*.py dosyalarını temizle (build_v2.py yeterli)
  - __pycache__ dizinlerini temizle
  - .pyc dosyalarını temizle
  - Gereksiz .md dosyalarını birleştir

Adım 6: Termux ortamını kontrol et
  - Python versiyonu: python --version
  - Node.js versiyonu: node --version (yoksa kur)
  - Git versiyonu: git --version
  - pip paketlerini listele: pip list
  - Disk alanı: df -h
  - RAM durumu: free -h

Adım 7: Mevcut Hermes yapılandırmasını incele
  - config.yaml dosyasını oku ve analiz et
  - .env dosyasını oku ve analiz et
  - Model ve provider ayarlarını kontrol et
  - Tool yapılandırmalarını kontrol et

Adım 8: Mevcut skill'leri listele - hangileri aktif, hangileri güncel değil
  - skills_list çalıştır
  - Her skill'in son güncelleme tarihini kontrol et
  - Eski veya bozuk skill'leri tespit et

Adım 9: Mevcut cron job'ları listele - hangileri çalışıyor
  - cronjob action='list' çalıştır
  - Her job'u durumunu kontrol et
  - Eski veya bozuk job'ları tespit et

Adım 10: Genel sistem sağlık raporu oluştur
  - Tüm bulguları özetle
  - Öncelik sıralaması yap
  - Hızlı düzeltmeler için yol haritası çıkar

## B. Yedekleme (Adım 11-20)

Adım 11: Tüm mevcut verileri yedekle - tar.gz olarak
  - /data/data/com.termux/files/home/anime-project/ dizinini sıkıştır
  - Tarih damgalı isimlendir: backup_YYYYMMDD_HHMMSS.tar.gz
  - Checksum oluştur (md5sum)

Adım 12: Hermes config dosyalarını yedekle
  - ~/.hermes/config.yaml yedekle
  - ~/.hermes/.env yedekle
  - ~/.hermes/skills/ dizinini yedekle
  - ~/.hermes/memory/ dizinini yedekle

Adım 13: Skill dosyalarını yedekle
  - Tüm skill SKILL.md dosyalarını kopyala
  - Script ve template dosyalarını kopyala
  - Skill bağımlılıklarını dokümante et

Adım 14: Memory dosyalarını yedekle
  - memory store dosyalarını kopyala
  - user profile dosyalarını kopyala
  - fact_store verilerini kopyala
  - session_search veritabanını kopyala

Adım 15: Cron job yapılandırmalarını yedekle
  - Tüm cron job'ların konfigürasyonunu JSON olarak kaydet
  - Bağlı skill ve prompt'ları kaydet
  - Schedule ayarlarını kaydet

Adım 16: GitHub token ve credential'ları güvenli yerde sakla
  - Token'ları şifreli dosyada sakla
  - .gitignore'a ekle
  - Erişim izinlerini kısıtla

Adım 17: Yedekleri GitHub'a pushla (private repo)
  - Private backup repo oluştur veya mevcut kullan
  - GPG şifreli olarak pushla
  - Commit mesajında tarih ve versiyon bilgisi olsun

Adım 18: Yedekleri yerel olarak da sakla - /sdcard/backup/
  - /sdcard/backup/ dizinini oluştur
  - Son 3 yedeği yerelde tut
  - Otomatik temizleme politikası belirle (30 günden eski sil)

Adım 19: Geri yükleme testi yap - temiz kurulum senaryosu
  - Sanal bir dizinde test et
  - Tüm verilerin geri geldiğini doğrula
  - Bütünlük kontrolü yap (checksum)

Adım 20: Yedekleme otomasyonu kur - cron job ile haftalık
  - Her Pazar gece yedekleme cron job'u oluştur
  - Otomatik temizleme (30 gün sonra eski yedekleri sil)
  - Yedekleme sonrası Telegram bildirimi gönder

## C. Yapılandırma (Adım 21-35)

Adım 21: Ana proje dizin yapısını tasarla
  - /src - Kaynak kodlar
  - /src/api - Backend API
  - /src/web - Frontend web arayüz
  - /src/scripts - Yardımcı scriptler
  - /src/self-improve - Kendini geliştirme modülü
  - /data - Veritabanı ve veri dosyaları
  - /data/db - SQLite veritabanları
  - /data/cache - Önbellek dosyaları
  - /data/export - Dışa aktarma dosyaları
  - /data/import - İçe aktarma dosyaları
  - /config - Yapılandırma dosyaları
  - /logs - Log dosyaları
  - /tests - Test dosyaları
  - /docs - Dokümantasyon
  - /assets - Görseller, fontlar, vs.
  - /backup - Yedekler

Adım 22: .gitignore dosyasını güncelle
  - *.pyc, __pycache__/ ekle
  - .env ekle
  - data/db/*.db ekle
  - node_modules/ ekle
  - .vscode/ ekle (opsiyonel)
  - *.log ekle
  - .DS_Store ekle
  - backup/ ekle

Adım 23: README.md yaz - proje açıklaması, kurulum, kullanım
  - Proje başlığı ve açıklaması
  - Özellik listesi
  - Ekran görüntüleri (placeholder)
  - Kurulum talimatları (Termux)
  - Kullanım kılavuzu
  - Katkı rehberi
  - Lisans bilgisi

Adım 24: LICENSE dosyası ekle (MIT)
  - MIT lisans metni
  - Copyright bilgisi
  - Yazar bilgisi

Adım 25: requirements.txt oluştur - Python bağımlılıkları
  - flask veya fastapi (web framework)
  - sqlite3 (veritabanı)
  - requests (HTTP istekleri)
  - beautifulsoup4 (web scraping)
  - Pillow (görsel işleme)
  - python-dotenv (environment)
  - pytest (test framework)
  - pylint (code linting)
  - black (code formatting)

Adım 26: package.json oluştur - Node.js bağımlılıkları (web arayüz için)
  - react veya vue (UI framework)
  - vite (build tool)
  - tailwindcss (styling)
  - axios (HTTP client)
  - chart.js (grafikler)
  - router (sayfa yönlendirme)
  - state management (pinia/zustand)

Adım 27: .env şablonu oluştur - environment değişkenleri
  - GITHUB_TOKEN
  - TELEGRAM_BOT_TOKEN
  - TELEGRAM_CHAT_ID
  - DATABASE_PATH
  - LOG_LEVEL
  - APP_SECRET_KEY
  - API_RATE_LIMIT

Adım 28: config.yaml şablonu oluştur - uygulama ayarları
  - Veritabanı ayarları
  - API ayarları
  - Web sunucu ayarları
  - Loglama ayarları
  - Cache ayarları
  - Theme ayarları (Lain default)
  - Dil ayarları

Adım 29: Docker yapılandırması opsiyonel olarak hazırla
  - Dockerfile
  - docker-compose.yml
  - .dockerignore
  - NOT: Termux'ta Docker çalışmaz, ama referans olsun

Adım 30: CI/CD pipeline şablonu oluştur (GitHub Actions)
  - .github/workflows/test.yml
  - .github/workflows/lint.yml
  - .github/workflows/deploy.yml
  - Otomatik test çalıştırma
  - Otomatik lint kontrolü
  - Release oluşturma

Adım 31: Issue şablonları oluştur
  - .github/ISSUE_TEMPLATE/bug_report.md
  - .github/ISSUE_TEMPLATE/feature_request.md
  - .github/ISSUE_TEMPLATE/task.md
  - Form alanları ve örnekler

Adım 32: Contributing guide yaz
  - Nasıl katkıda bulunulur
  - Kod standartları
  - Commit mesaj formatı
  - PR süreci
  - Test gereksinimleri

Adım 33: Code of Conduct ekle
  - Davranış kuralları
  - İletişim standartları
  - İhlal durumu prosedürü

Adım 34: Security policy yaz
  - Güvenlik açığı bildirme prosedürü
  - Güvenlik güncelleme politikası
  - Desteklenen versiyonlar

Adım 35: Changelog formatı belirle (Keep a Changelog)
  - CHANGELOG.md oluştur
  - Versiyon numlandırması (semver)
  - Değişiklik kategorileri (Added, Changed, Fixed, Removed)

## D. Geliştirme Ortamı (Adım 36-50)

Adım 36: Python virtual environment oluştur ve yapılandır
  - python -m venv venv
  - venv aktifleştir: source venv/bin/activate
  - pip install -r requirements.txt
  - .gitignore'a venv/ ekle

Adım 37: Node.js ortamını kur ve yapılandır (web arayüz için)
  - npm init -y
  - Bağımlılıkları kur
  - vite projesi oluştur
  - tailwindcss yapılandır

Adım 38: SQLite veritabanı şemasını tasarla
  - films tablosu (id, title, year, director, studio, mal_score, imdb_score, owl_score, source_material, synopsis_tr, synopsis_en, poster_url, trailer_url, duration, age_rating, budget, revenue, animation_type, aspect_ratio, sound_format, color, created_at, updated_at)
  - users tablosu (id, username, email, password_hash, avatar_url, bio, created_at, last_login, is_active, role)
  - watchlist tablosu (id, user_id, film_id, status, watch_date, watch_count, last_watched, platform, personal_note, personal_rating, personal_review, is_favorite, is_hidden, is_archived, tags, mood, watched_with, watch_location, watch_type, progress_percent, created_at, updated_at)
  - ratings tablosu (id, user_id, film_id, rating, created_at, updated_at)
  - reviews tablosu (id, user_id, film_id, review_text, is_spoiler, likes, created_at, updated_at)
  - genres tablosu (id, name_tr, name_en, slug, description)
  - film_genres tablosu (film_id, genre_id)
  - directors tablosu (id, name, birth_date, nationality, bio, photo_url)
  - film_directors tablosu (film_id, director_id)
  - studios tablosu (id, name, country, founded_year, logo_url, website)
  - film_studios tablosu (film_id, studio_id)
  - web_novels tablosu (id, title, author, platform, status, chapters, genre, synopsis, url, anime_adaptation, anime_quality, wn_score, created_at)
  - light_novels tablosu (id, title, author, illustrator, publisher, status, volumes, genre, synopsis, url, anime_adaptation, anime_quality, ln_score, created_at)
  - manga tablosu (id, title, author, artist, publisher, status, volumes, chapters, genre, synopsis, url, anime_adaptation, anime_quality, manga_score, created_at)
  - adaptations tablosu (id, source_type, source_id, adaptation_type, adaptation_id, quality_score, faithfulness_score)
  - platforms tablosu (id, name, url, logo_url, type, region, is_active)
  - film_platforms tablosu (film_id, platform_id, url, price, available_from, available_until)
  - recommendations tablosu (id, user_id, film_id, score, reason, algorithm, is_clicked, is_watched, created_at)
  - user_preferences tablosu (id, user_id, preference_key, preference_value, weight, updated_at)
  - search_history tablosu (id, user_id, query, filters, result_count, created_at)
  - activity_log tablosu (id, user_id, action, target_type, target_id, details, ip_address, user_agent, created_at)
  - system_log tablosu (id, level, component, message, details, created_at)
  - performance_log tablosu (id, metric_name, metric_value, context, created_at)
  - error_log tablosu (id, error_type, error_message, stack_trace, context, severity, is_resolved, resolved_at, created_at)
  - backup_log tablosu (id, backup_type, file_path, file_size, checksum, status, started_at, completed_at)
  - memory_store tablosu (id, memory_type, content, source, importance_score, access_count, last_accessed, created_at, updated_at, is_compressed)
  - settings tablosu (id, key, value, value_type, description, is_public, updated_at)

Adım 39: Redis cache opsiyonunu değerlendir
  - Termux'ta Redis kurulabilir mi araştır
  - Gerekirse SQLite tabanlı cache sistemi yaz
  - Cache invalidation stratejisi belirle

Adım 40: Loglama sistemini kur (Python logging)
  - Dosya tabanlı loglama (rotating file handler)
  - Konsol loglama (stream handler)
  - JSON format loglama
  - Log seviyeleri: DEBUG, INFO, WARNING, ERROR, CRITICAL
  - Log rotasyonu: günlük, 10MB limit
  - Log sıkıştırma: gzip

Adım 41: Hata yakalama ve raporlama sistemini kur
  - Global exception handler
  - Try-catch pattern standardizasyonu
  - Hata detayları toplama (stack trace, context, timestamp)
  - Otomatik hata raporu oluşturma
  - Telegram bildirim entegrasyonu (kritik hatalar için)

Adım 42: Test framework'ü kur (pytest)
  - pytest yapılandırması (pytest.ini)
  - Fixture'lar oluştur (veritabanı, API client)
  - Unit test şablonu
  - Integration test şablonu
  - Test coverage aracı (pytest-cov)

Adım 43: Code formatter yapılandır (black, prettier)
  - black yapılandırması (pyproject.toml)
  - prettier yapılandırması (package.json)
  - Pre-commit hook ile otomatik formatlama
  - Editor entegrasyonu ayarları

Adım 44: Linter yapılandır (flake8, eslint)
  - flake8 yapılandırması (.flake8)
  - eslint yapılandırması (.eslintrc.json)
  - Git hook ile otomatik kontrol
  - CI/CD pipeline'da otomatik kontrol

Adım 45: Git hooks kur (pre-commit, pre-push)
  - pre-commit: lint + format kontrolü
  - pre-push: test çalıştırma
  - commit-msg: commit mesaj format kontrolü
  - hook scriptlerini yaz

Adım 46: IDE/editor yapılandırması oluştur (.vscode/)
  - settings.json (format on save, linter, vs.)
  - extensions.json (önerilen eklentiler)
  - launch.json (debug yapılandırması)
  - tasks.json (görev tanımları)

Adım 47: Debug yapılandırması hazırla
  - Python debugger (pdb / debugpy)
  - Flask/FastAPI debug modu
  - Veritabanı query profiler
  - API request/response logger

Adım 48: Profil oluşturma araçlarını kur (cProfile, line_profiler)
  - cProfile yapılandırması
  - line_profiler yapılandırması
  - memory_profiler yapılandırması
  - Profil sonuçlarını görselleştirme

Adım 49: Token sayacı ve optimizasyon aracı kur
  - Token kullanım takibi
  - Günlük/aylık token raporu
  - Token bütçesi belirleme
  - Otomatik token optimizasyonu önerileri

Adım 50: Geliştirme ortamı sağlık kontrolü yap
  - Tüm araçların çalıştığını doğrula
  - Test suite'ini çalıştır
  - Linter ve formatter'ları çalıştır
  - Yedekleme scriptini test et

================================================================================
# FAZ 1: VERİTABANI VE VERİ MİMARİSİ (Adım 51-200)
================================================================================

## A. Veritabanı Oluşturma ve Migration (Adım 51-80)

Adım 51: SQLite veritabanı dosyasını oluştur
  - /data/db/owl_anime.db oluştur
  - WAL mode aktifleştir (performans için)
  - Foreign key desteğini aktifleştir
  - Charset: UTF-8

Adım 52: films tablosunu oluştur (tüm alanlarla)
  - PRIMARY KEY (id INTEGER AUTOINCREMENT)
  - UNIQUE constraint (title, year)
  - INDEX: year, mal_score, owl_score, director, studio
  - CHECK constraints: mal_score 0-10, imdb_score 0-10

Adım 53: users tablosunu oluştur
  - PRIMARY KEY, UNIQUE username/email
  - Password hash (bcrypt)
  - Role-based access (admin, user, guest)
  - Default values ve constraints

Adım 54: watchlist tablosunu oluştur
  - Composite UNIQUE (user_id, film_id)
  - Foreign keys ve cascade rules
  - Status enum: watching, completed, planning, paused, dropped, hidden
  - INDEX: user_id, status, watch_date, is_favorite

Adım 55: ratings tablosunu oluştur
  - Composite UNIQUE (user_id, film_id)
  - CHECK: rating 0-10
  - Foreign keys

Adım 56: reviews tablosunu oluştur
  - Foreign keys, cascade delete
  - Full-text search index (review_text)
  - CHECK: length <= 10000 karakter

Adım 57: tags tablosunu oluştur
  - UNIQUE slug
  - Kategori: genre, theme, mood, custom

Adım 58: film_tags tablosunu oluştur
  - Composite PRIMARY KEY (film_id, tag_id)
  - Foreign keys

Adım 59: web_novels tablosunu oluştur
  - Tüm alanlarla (title, author, platform, status, chapters, genre, synopsis, url, anime_adaptation, wn_score)
  - INDEX: platform, status, wn_score
  - Platform enum: syosetu, kakuyomu, alphapolis, hameln, pixiv, royalroad, webnovel, wuxiaworld, novelupdates

Adım 60: light_novels tablosunu oluştur
  - Tüm alanlarla (title, author, illustrator, publisher, status, volumes, genre, synopsis, url, anime_adaptation, ln_score)
  - INDEX: publisher, status, ln_score

Adım 61: manga tablosunu oluştur
  - Tüm alanlarla (title, author, artist, publisher, status, volumes, chapters, genre, synopsis, url, anime_adaptation, manga_score)
  - INDEX: publisher, status, manga_score

Adım 62: adaptations tablosunu oluştur
  - Source → adaptation mapping
  - Quality ve faithfulness score
  - Adaptation type: direct, loose, inspired, spin-off, prequel, sequel

Adım 63: platforms tablosunu oluştur
  - İlk platformları ekle: Netflix, Crunchyroll, Funimation, Amazon Prime, Hulu, Disney+, HIDIVE, RetroCrush, YouTube, Bilibili, iQIYI, Plex, local files
  - Platform türü: streaming, download, theatrical, physical

Adım 64: film_platforms tablosunu oluştur
  - Composite UNIQUE (film_id, platform_id)
  - URL, price, availability dates
  - Free/paid/subscription indicator

Adım 65: recommendations tablosunu oluştur
  - User-film mapping with score
  - Algorithm tag (content-based, collaborative, hybrid)
  - Feedback tracking (clicked, watched, ignored)

Adım 66: user_preferences tablosunu oluştur
  - Key-value store for preferences
  - Weight for each preference
  - Categories: genre_pref, mood_pref, era_pref, length_pref, studio_pref, director_pref

Adım 67: search_history tablosunu oluştur
  - Query log with filters
  - Result count tracking
  - Full-text index on query

Adım 68: activity_log tablosunu oluştur
  - User activity tracking
  - Action types: view, search, rate, review, add_watchlist, mark_watched, hide, archive
  - Partitioning strategy (monthly)

Adım 69: system_log tablosunu oluştur
  - System event logging
  - Component-based categorization
  - Auto-cleanup policy (90 days)

Adım 70: performance_log tablosunu oluştur
  - Metric name, value, context
  - Response times, query times, API calls
  - Aggregation support (min, max, avg, p95, p99)

Adım 71: error_log tablosunu oluştur
  - Detailed error tracking
  - Stack trace storage
  - Resolution tracking (is_resolved, resolved_at)
  - Severity levels: low, medium, high, critical

Adım 72: backup_log tablosunu oluştur
  - Backup operation tracking
  - File path, size, checksum
  - Status: started, completed, failed
  - Timing information

Adım 73: memory_store tablosunu oluştur
  - Short-term, long-term, episodic, semantic memory types
  - Compression support (is_compressed)
  - Importance scoring (0-1)
  - Access pattern tracking (count, last_accessed)

Adım 74: settings tablosunu oluştur
  - Key-value store for application settings
  - Type enforcement (string, int, float, boolean, json)
  - Public/private flag

Adım 75: Migration sistemi oluştur
  - migration_log tablosu
  - Versiyon numlandırması
  - Up/down migration desteği
  - Checksum doğrulama

Adım 76: İlk migration'ları yaz (001_initial_schema.sql)
  - Tüm tablo CREATE statement'ları
  - Index CREATE statement'ları
  - Foreign key constraints
  - Default değerler

Adım 77: Seed data yaz
  - Default settings
  - Default genres (17 tür)
  - Default platforms (14 platform)
  - Default admin user
  - Default theme settings (Lain)

Adım 78: Migration çalıştırma scripti yaz
  - Python tabanlı migration runner
  - Transaction desteği (rollback on error)
  - Progress reporting
  - Dry-run mode

Adım 79: Veritabanı bağlantı yöneticisi yaz (connection manager)
  - Connection pooling
  - Context manager desteği (with statement)
  - Automatic retry logic
  - Query timeout
  - WAL mode ve optimizasyon ayarları

Adım 80: ORM benzeri basit query builder yaz
  - Tablo bazlı CRUD operasyonlar
  - WHERE, ORDER BY, LIMIT, OFFSET desteği
  - JOIN desteği
  - Aggregation functions (COUNT, SUM, AVG, MIN, MAX)
  - Full-text search wrapper

## B. Veri Göçü (Migration) (Adım 81-110)

Adım 81: Mevcut JSON verileri analiz et
  - analyzed_films.json yapısını incele
  - Eksik alanları tespit et
  - Tutarsızlıkları tespit et
  - Veri kalitesi raporu oluştur

Adım 82: 215 filmi veritabanına aktar (films tablosu)
  - JSON → SQL dönüşümü
  - Duplicate kontrolü
  - NULL handling
  - Batch insert (100'erli gruplar)

Adım 83: Tür bilgilerini normalize et ve aktar
  - film_genres tablosunu doldur
  - genres tablosunu doldur (17 tür)
  - Many-to-many ilişkilerini kur
  - Kategori eşleştirmelerini doğrula

Adım 84: Yönetmen bilgilerini normalize et ve aktar
  - Benzersiz yönetmenleri çıkar
  - directors tablosunu doldur
  - film_directors tablosunu doldur
  - Multi-director filmleri işle

Adım 85: Stüdyo bilgilerini normalize et ve aktar
  - Benzersiz stüdyoları çıkar
  - studios tablosunu doldur
  - film_studios tablosunu doldur

Adım 86: Kaynak malzeme bilgilerini normalize et ve aktar
  - Her film için source_material alanını doldur
  - Kaynak türlerini sınıflandır: Manga, Light Novel, Web Novel, Visual Novel, Original, Novel, Folklore, Game, TV Series

Adım 87: Web novel bağlantılarını ekle
  - web_novels tablosunu doldur
  - İlk 50 web novel ekle (en popüler olanlar)
  - Uyarlamaları adaptations tablosuna ekle

Adım 88: Platform bilgilerini ekle
  - platforms tablosunu doldur (14 platform)
  - Her film için uygun platformları ekle
  - film_platforms tablosunu doldur

Adım 89: Mevcut izlenen listesini aktar
  - watched.txt'den oku
  - watchlist tablosuna aktar (status=completed)
  - user_id=1 (default admin)

Adım 90: Kullanıcı tablosunu doldur
  - Default admin user oluştur
  - user_preferences tablosunu doldur (zevk profili)
  - Tür ağırlıklarını ekle (action_epic: 9, philosophical_surreal: 10, vs.)

Adım 91: Veri bütünlüğünü doğrula
  - Foreign key kontrolleri
  - NULL check
  - Range check (puanlar 0-10 arası mı)
  - Duplicate check
  - Orphan record check

Adım 92: Format ve encoding kontrolleri
  - Türkçe karakter doğrulaması
  - UTF-8 encoding kontrolü
  - Tarih formatı kontrolü
  - URL format kontrolü

Adım 93: İstatistiksel analiz yap
  - Toplam film sayısı
  - Tür dağılımı
  - Yıl dağılımı
  - Puan dağılımı
  - Kaynak malzeme dağılımı
  - Eksik veri istatistiği

Adım 94: Eksik veri tespit ve tamamlama planı
  - Hangi filmde hangi alan eksik
  - Otomatik tamamlama kaynakları (MAL API, AniDB API)
  - Manuel tamamlama gerekenler
  - Öncelik sıralaması

Adım 95: Veritabanı backup'ı al
  - .dump dosyası oluştur
  - SQLite backup API kullan
  - Checksum oluştur

Adım 96: Migration scripti yaz (geri alma dahil)
  - Her migration için up() ve down() fonksiyonu
  - Transaction içinde çalıştır
  - Hata durumunda otomatik rollback

Adım 97: Migration testi yap
  - Clean database'te migration çalıştır
  - Tüm verilerin doğru geldiğini doğrula
  - Geri alma testi yap (down migration)
  - Checksum karşılaştırma

Adım 98: Performans testi yap (sorgu süreleri)
  - SELECT sorgu süreleri (ortalama, min, max)
  - INSERT sorgu süreleri
  - UPDATE sorgu süreleri
  - DELETE sorgu süreleri
  - JOIN sorgu süreleri
  - Full-text search süreleri

Adım 99: Index optimizasyonu yap
  - Kullanılmayan index'leri tespit et
  - Eksik index'leri ekle
  - Composite index'leri optimize et
  - Query EXPLAIN analizi

Adım 100: VACUUM ve ANALYZE çalıştır
  - Database file size optimization
  - Query planner optimization
  - Statistics update

Adım 101: Veri kalitesi skoru hesapla
  - Her film için completeness score (0-100)
  - Tablo bazlı kalite skoru
  - Genel veritabanı kalite raporu

Adım 102: Eksik veri raporu oluştur
  - Hangi filmlerde hangi alanlar eksik
  - Otomatik tamamlanabilir alanlar
  - Manuel gereken alanlar
  - Tahmini tamamlama süresi

Adım 103: Otomatik veri tamamlama scripti yaz
  - MAL API'den film bilgileri çek
  - AniDB'den ek bilgiler çek
  - IMDb'den rating bilgileri çek
  - Poster/trailer URL'leri çek
  - Rate limiting ve hata yönetimi

Adım 104: Manuel veri tamamlama aracı oluştur
  - CLI tabanlı interaktif araç
  - Film bilgilerini düzenleme
  - Toplu düzenleme desteği
  - Değişiklik geçmişi

Adım 105: Veri doğrulama testleri yaz
  - pytest fixture'ları
  - Her tablo için validation testleri
  - Constraint testleri
  - Foreign key testleri
  - Data type testleri

Adım 106: Veri bütünlük testleri yaz
  - Orphan record testleri
  - Duplicate testleri
  - Range testleri
  - Format testleri
  - Referential integrity testleri

Adım 107: Performans testleri yaz
  - Query süre testleri
  - Concurrent access testleri
  - Large dataset testleri
  - Memory usage testleri

Adım 108: Yedekleme testi yap
  - Backup oluştur
  - Restore et
  - Veri bütünlüğünü doğrula
  - Performans karşılaştırması

Adım 109: Geri yükleme testi yap
  - Clean slate'ten başla
  - Yedekten geri yükle
  - Tüm verilerin doğru geldiğini doğrula
  - Migration'ların çalıştığını doğrula

Adım 110: Veritabanı sağlık raporu oluştur
  - Toplam tablo sayısı
  - Toplam kayıt sayısı
  - Database boyutu
  - Eksik veri istatistikleri
  - Performans metrikleri
  - Öneriler

## C. Veri Zenginleştirme (Adım 111-150)

Adım 111: Her film için poster URL'si ekle
  - MAL API'den poster URL çek
  - TMDb API'den poster URL çek
  - Fallback: placeholder image
  - Local cache için indirme

Adım 112: Her film için trailer URL'si ekle
  - YouTube API'den trailer çek
  - MAL'den trailer linki çek
  - Embed URL formatında sakla

Adım 113: Her film için süre bilgisi ekle
  - MAL API'den duration çek
  - Dakika cinsinden sakla
  - Short film (<40dk) vs feature film ayrımı

Adım 114: Her film için yayın tarihi detayı ekle
  - Gün/ay/yıl formatında sakla
  - İlk gösterim tarihi (Japan release date)
  - Uluslararası gösterim tarihi

Adım 115: Her film için yaş sınırı bilgisi ekle
  - Japanese rating (G, PG12, R15+, R18+)
  - International rating equivalent
  - Content warnings

Adım 116: Her film için bütçe bilgisi ekle (varsa)
  - ABD doları cinsinden
  - Kaynak belirt
  - Tahmini değerler için "estimated" flag

Adım 117: Her film için hasılat bilgisi ekle (varsa)
  - Global box office
  - Japan box office
  - USD cinsinden

Adım 118: Her film için ödül bilgisi ekle
  - Academy Award
  - Annie Award
  - Japan Academy Prize
  - Annecy Cristal
  - Berlin Golden Bear
  - Cannes selection
  - Mainichi Film Award

Adım 119: Her film için MAL ID'si ekle
  - MyAnimeList anime_id
  - URL: https://myanimelist.net/anime/{id}

Adım 120: Her film için AniDB ID'si ekle
  - AniDB anime_id
  - URL: https://anidb.net/anime/{id}

Adım 121: Her film için IMDb ID'si ekle
  - IMDb tt_id
  - URL: https://www.imdb.com/title/{id}

Adım 122: Her film için TMDb ID'si ekle
  - TMDb movie_id
  - URL: https://www.themoviedb.org/movie/{id}

Adım 123: Her film için Tags/Keywords ekle
  - MAL tags
  - User-defined tags
  - Content tags (violence, romance, etc.)
  - Theme tags (coming-of-age, war, etc.)

Adım 124: Her film için Türkçe synopsis/özet ekle
  - MAL'den Türkçe açıklama çek
  - Wikipedia'dan Türkçe özet çek
  - 200-500 kelime arası
  - Spoiler warning desteği

Adım 125: Her film için İngilizce synopsis/özet ekle
  - MAL'den İngilizce açıklama çek
  - ANN'den İngilizce özet çek
  - 200-500 kelime arası

Adım 126: Her film için karakter listesi ekle
  - Ana karakterler (isim, rol, seslendirici)
  - Destekleyici karakterler
  - Karakter tipleri (protagonist, antagonist, supporting)

Adım 127: Her film için seslendirme bilgisi ekle (JP)
  - Japonca orijinal seslendirme
  - Başroller ve seslendiriciler
  - Ekibin önceki çalışmaları

Adım 128: Her film için seslendirme bilgisi ekle (EN)
  - İngilizce dub seslendirme
  - Funimation/Crunchyroll/A-1 dubları
  - Başroller ve seslendiriciler

Adım 129: Her film için müzik bilgisi ekle
  - Besteci/composer
  - Müzik stüdyosu
  - Japonca/İngilizce müzik farkları

Adım 130: Her film için senarist bilgisi ekle
  - Senaryo yazarı
  - Hikaye/Storyboard
  - Orijinal eser yazarı (varsa)

Adım 131: Her film için yapım süresi bilgisi ekle
  - Toplam yapım süresi
  - Animasyon yapım süresi
  - Yayın öncesi süreç

Adım 132: Her film için teknik detaylar ekle
  - Animasyon türü (2D, 3D, stop-motion, mixed)
  - Renk teknolojisi (color, B&W, partial color)
  - Çözünürlük (SD, HD, 4K)
  - Ses formatı (mono, stereo, 5.1, 7.1)

Adım 133: Her film için aspect ratio ekle
  - 4:3 (1.33:1)
  - 16:9 (1.78:1)
  - 2.35:1 (anamorphic)
  - IMAX

Adım 134: Her film için lisans bilgisi ekle
  - Japon lisans sahibi
  - Uluslararası lisans sahibi
  - Lisans durumu (aktif, süresi doldu)

Adım 135: Her film için franchise/seri bilgisi ekle
  - Franchise adı
  - Seri içindeki konum
  - Bağlantılı filmler
  - Shared universe bilgisi

Adım 136: Her film için sequel/prequel bilgisi ekle
  - Önceki film (prequel)
  - Sonraki film (sequel)
  - Timeline pozisyonu

Adım 137: Her film için spin-off bilgisi ekle
  - Ana seri
  - Spin-off türü (side story, gaiden, alternate universe)
  - Bağlantı derecesi

Adım 138: Her film için remake bilgisi ekle
  - Orijinal film
  - Remake tarihi
  - Farklılıklar

Adım 139: Her film için fan art/community bilgisi ekle
  - Fan art sayısı (tahmini)
  - Cosplay popülerliği
  - Meme/varlık popülerliği
  - Reddit/Discord topluluk büyüklüğü

Adım 140: Her film için trivia/ilginç bilgi ekle
  - Prodüksiyon trivia
  - Gizli detaylar (easter eggs)
  - Kültürel referanslar
  - Etkilenmiş eserler

Adım 141: Her film için famous quote/söz ekle
  - En ünlü replikler
  - Japonca orijinal + Türkçe çeviri
  + İngilizce çeviri

Adım 142: Her film için soundtrack listesi ekle
  - Japonça opening/ending şarkıları
  - Besteci/Artist bilgisi
  - Albüm bilgisi
  - Spotify/Apple Music linki

Adım 143: Her film için episode sayısı ekle (film ise 1)
  - Film için: 1
  - OVA serisi için: bölüm sayısı
  - Split film için: parça sayısı

Adım 144: Her film için bölüm süresi ekle
  - Tek film: toplam süre
  - Seri: ortalama bölüm süresi
  - Varyasyon aralığı

Adım 145: Her film için toplam süre ekle
  - Dakika cinsinden
  - Saat:dakika formatında gösterim
  - Seri için toplam süre

Adım 146: Her film için bütçe/hasırat oranı hesapla
  - ROI (Return on Investment)
  - Başarı metriği (hit, moderate, flop)
  - Dönemsel karşılaştırma

Adım 147: Her film için kritik özet ekle
  - Rottentomatoes skoru
  - Metacritic skoru
  - Kritik ortalaması
  - "Fresh" veya "Rotten" durumu

Adım 148: Her film için izleyici demografisi ekle
  - Yaş dağılımı
  - Cinsiyet dağılımı
  - Coğrafi dağılım
  - Hedef kitle analizi

Adım 149: Her film için karşılaştırma özellikleri ekle
  - Benzer filmler (content-based)
  - Aynı yöntmen filmleri
  - Aynı stüdyo filmleri
  - Aynı dönem filmleri

Adım 150: Veri zenginleştirme raporu oluştur
  - Tamamlanan alanlar
  - Eksik alanlar
  - Otomatik tamamlanabilir alanlar
  - Manuel gereken alanlar
  - Tahmini tamamlama süresi

## D. Veri Doğrulama (Adım 151-170)

Adım 151: Tüm URL'leri erişilebilirlik kontrolü
  - HTTP status code kontrolü (200, 301, 404)
  - Dead link tespiti
  - Yedek URL bulma
  - Rate limiting uyumu

Adım 152: Tüm tarih formatlarını standartlaştır
  - ISO 8601 formatı (YYYY-MM-DD)
  - Yıl için: YYYY
  - Gün ay yıl için: DD/MM/YYYY
  - Tarih geçerliliği kontrolü

Adım 153: Türkçe karakter sorunlarını düzelt
  - Ş, ş, Ğ, ğ, İ, ı, Ö, ö, Ü, ü, Ç, ç
  - Encoding kontrolü (UTF-8)
  - Bozulmuş karakter onarımı
  - Normalizasyon

Adım 154: Boş alanları tespit et ve doldur
  - NULL vs empty string ayrımı
  - Zorunlu alanların doluluk oranı
  - Opsiyonel alanların doluluk oranı
  - Eksik veri önceliklendirme

Adım 155: Tutarsız verileri tespit et ve düzelt
  - Aynı film farklı isimlerle
  - Çelişen puanlar
  - Hatalı yıl bilgileri
  - Yanlış tür atamaları

Adım 156: Puan aralıklarını doğrula (0-10)
  - MAL puanları 0-10 arası
  - IMDb puanları 0-10 arası
  - OWL puanları 0-10 arası
  - Outlier tespiti

Adım 157: Yıl değerlerini doğrula
  - Minimum: 1917 (ilk Japon animasyonu)
  - Maksimum: 2026 (güncel)
  - Gelecek tarih kontrolü
  - Tarih çakışması kontrolü

Adım 158: Duplicate kontrolü yap (farklı kaynaklardan)
  - Aynı film farklı isimlerle
  - Farklı yıllarda aynı isim
  - Çoklu stüdyo filmleri
  - Merge/plit kararları

Adım 159: Cross-reference kontrolü yap
  - MAL ID doğrulama
  - IMDb ID doğrulama
  - TMDb ID doğrulama
  - AniDB ID doğrulama
  - URL çalışabilirlik kontrolü

Adım 160: Veri kalitesi skoru hesapla
  - Her film için completeness score (0-100)
  - Tablo bazlı kalite skoru
  - Genel veritabanı kalite raporu
  - İyileştirme önerileri

Adım 161: Eksik veri raporu oluştur
  - Hangi filmde hangi alanlar eksik
  - Eksik veri yüzdeleri
  - Etkilenen sorgular
  - Tamamlama öncelikleri

Adım 162: Veri tamamlama planı oluştur
  - Otomatik tamamlanabilir alanlar
  - Manuel gereken alanlar
  - Kaynak belirleme
  - Tahmini süre
  - Öncelik sıralaması

Adım 163: Otomatik veri tamamlama scripti yaz
  - MAL API entegrasyonu
  - AniDB API entegrasyonu
  - IMDb scraping (rate-limited)
  - TMDb API entegrasyonu
  - Wikipedia scraping
  - hata yönetimi ve retry logic

Adım 164: Manuel veri tamamlama aracı oluştur
  - CLI tabanlı interaktif araç
  - Film seçimi ve düzenleme
  - Toplu düzenleme
  - Değişiklik preview
  - Undo/redo desteği

Adım 165: Veri doğrulama testleri yaz
  - pytest fixture'lar
  - Her tablo için validation testleri
  - Constraint testleri
  - Foreign key testleri
  - Data type testleri

Adım 166: Veri bütünlük testleri yaz
  - Orphan record testleri
  - Duplicate testleri
  - Range testleri
  - Format testleri
  - Referential integrity testleri

Adım 167: Performans testleri yaz
  - Query süre testleri
  - Concurrent access testleri
  - Large dataset testleri
  - Memory usage testleri
  - Scalability testleri

Adım 168: Yedekleme testi yap
  - Backup oluştur
  - Restore et
  - Veri bütünlüğünü doğrula
  - Performans karşılaştırması
  - Recovery time measurement

Adım 169: Geri yükleme testi yap
  - Clean slate'ten başla
  - Yedekten geri yükle
  - Tüm verilerin doğru geldiğini doğrula
  - Migration'ların çalıştığını doğrula
  - Performance benchmark

Adım 170: Veritabanı sağlık raporu oluştur
  - Toplam tablo sayısı
  - Toplam kayıt sayısı
  - Database boyutu (MB)
  - Eksik veri istatistikleri
  - Performans metrikleri
  - Index kullanım istatistikleri
  - Öneriler

## E. API Katmanı (Adım 171-200)

Adım 171: REST API tasarımı yap (OpenAPI/Swagger)
  - Endpoint listesi
  - Request/response şemaları
  - Authentication flow
  - Error response formatları
  - Rate limiting
  - Pagination standardı
  - Filtering/sorting standardı

Adım 172: Film CRUD API'leri yaz
  - GET /api/films - Tüm filmler (paginated)
  - GET /api/films/{id} - Tek film detay
  - POST /api/films - Yeni film ekle
  - PUT /api/films/{id} - Film güncelle
  - DELETE /api/films/{id} - Film sil
  - PATCH /api/films/{id} - Kısmi güncelleme

Adım 173: Arama API'si yaz (full-text search)
  - GET /api/search?q={query}
  - Full-text search (başlık, özet, yönetmen)
  - Fuzzy search (hatalı yazım toleransı)
  - Search suggestions
  - Search highlighting

Adım 174: Filtreleme API'si yaz (tür, yıl, puan, vs.)
  - GET /api/films?genre={genre}
  - GET /api/films?year_from={year}&year_to={year}
  - GET /api/films?min_score={score}&max_score={score}
  - GET /api/films?studio={studio}
  - GET /api/films?director={director}
  - GET /api/films?source={source}
  - GET /api/films?platform={platform}

Adım 175: Sıralama API'si yaz
  - GET /api/films?sort=owl_score&order=desc
  - GET /api/films?sort=year&order=desc
  - GET /api/films?sort=mal_score&order=desc
  - GET /api/films?sort=title&order=asc
  - GET /api/films?sort=random
  - Multi-field sorting desteği

Adım 176: Sayfalama API'si yaz
  - GET /api/films?page={page}&limit={limit}
  - Cursor-based pagination
  - Offset-based pagination
  - Total count header
  - HATEOAS link headers

Adım 177: Kullanıcı API'leri yaz
  - POST /api/auth/register - Kayıt
  - POST /api/auth/login - Giriş
  - POST /api/auth/logout - Çıkış
  - POST /api/auth/refresh - Token yenileme
  - GET /api/users/me - Profil
  - PUT /api/users/me - Profil güncelle
  - PUT /api/users/me/password - Şifre değiştir
  - DELETE /api/users/me - Hesap sil

Adım 178: Watchlist API'leri yaz
  - GET /api/watchlist - İzleme listesi
  - POST /api/watchlist - Listeye ekle
  - PUT /api/watchlist/{film_id} - Güncelle
  - DELETE /api/watchlist/{film_id} - Listeden çıkar
  - GET /api/watchlist/status/{status} - Duruma göre filtrele
  - POST /api/watchlist/batch - Toplu işlem
  - GET /api/watchlist/stats - İzleme istatistikleri

Adım 179: Puanlama API'leri yaz
  - POST /api/ratings - Puan ver
  - PUT /api/ratings/{film_id} - Puan güncelle
  - DELETE /api/ratings/{film_id} - Puan sil
  - GET /api/ratings/{film_id} - Film puanları
  - GET /api/ratings/user/me - Benim puanlarım

Adım 180: Yorum API'leri yaz
  - GET /api/reviews/{film_id} - Film yorumları
  - POST /api/reviews - Yorum yaz
  - PUT /api/reviews/{id} - Yorum güncelle
  - DELETE /api/reviews/{id} - Yorum sil
  - POST /api/reviews/{id}/like - Beğeni
  - POST /api/reviews/{id}/report - Şikayet

Adım 181: Öneri API'si yaz
  - GET /api/recommendations - Kişiselleştirilmiş öneriler
  - GET /api/recommendations/similar/{film_id} - Benzer filmler
  - GET /api/recommendations/trending - Trend filmler
  - GET /api/recommendations/unexplored - Keşfedilmemiş filmler
  - GET /api/recommendations/random - Rastgele öneri

Adım 182: İstatistik API'leri yaz
  - GET /api/stats/overview - Genel istatistikler
  - GET /api/stats/genres - Tür dağılımı
  - GET /api/stats/years - Yıl dağılımı
  - GET /api/stats/scores - Puan dağılımı
  - GET /api/stats/platforms - Platform dağılımı
  - GET /api/stats/user/stats - Kullanıcı istatistikleri

Adım 183: Admin API'leri yaz
  - GET /api/admin/users - Kullanıcı listesi
  - PUT /api/admin/users/{id}/role - Rol değiştir
  - DELETE /api/admin/users/{id} - Kullanıcı sil
  - GET /api/admin/logs - Sistem logları
  - GET /api/admin/stats - Sistem istatistikleri
  - POST /api/admin/backup - Yedekleme başlat
  - POST /api/admin/restore - Geri yükleme
  - DELETE /api/admin/cache - Cache temizle

Adım 184: Web Novel API'leri yaz
  - GET /api/webnovels - Web novel listesi
  - GET /api/webnovels/{id} - Web novel detay
  - GET /api/webnovels/search - Web novel arama
  - GET /api/webnovels/platform/{platform} - Platforma göre
  - GET /api/webnovels/status/{status} - Duruma göre
  - GET /api/webnovels/genre/{genre} - Türe göre

Adım 185: Light Novel API'leri yaz
  - GET /api/lightnovels - Light novel listesi
  - GET /api/lightnovels/{id} - Light novel detay
  - GET /api/lightnovels/search - Light novel arama
  - GET /api/lightnovels/publisher/{publisher} - Yayıncıya göre
  - GET /api/lightnovels/status/{status} - Duruma göre

Adım 186: Manga API'leri yaz
  - GET /api/manga - Manga listesi
  - GET /api/manga/{id} - Manga detay
  - GET /api/manga/search - Manga arama
  - GET /api/manga/demographic/{demo} - Demografiye göre
  - GET /api/manga/status/{status} - Duruma göre

Adım 187: Platform API'leri yaz
  - GET /api/platforms - Platform listesi
  - GET /api/platforms/{id} - Platform detay
  - GET /api/platforms/{id}/films - Platformdaki filmler
  - GET /api/platforms/compare - Platform karşılaştırma

Adım 188: Tür API'leri yaz
  - GET /api/genres - Tür listesi
  - GET /api/genres/{id} - Tür detay
  - GET /api/genres/{id}/films - Türdeki filmler
  - GET /api/genres/stats - Tür istatistikleri

Adım 189: Yönetmen API'leri yaz
  - GET /api/directors - Yönetmen listesi
  - GET /api/directors/{id} - Yönetmen detay
  - GET /api/directors/{id}/films - Yönetmenin filmleri
  - GET /api/directors/stats - Yönetmen istatistikleri

Adım 190: Stüdyo API'leri yaz
  - GET /api/studios - Stüdyo listesi
  - GET /api/studios/{id} - Stüdyo detay
  - GET /api/studios/{id}/films - Stüdyonun filmleri
  - GET /api/studios/stats - Stüdyo istatistikleri

Adım 191: Rate limiting ekle
  - IP bazlı rate limiting
  - Kullanıcı bazlı rate limiting
  - Endpoint bazlı rate limiting
  - Sliding window algoritması
  - Rate limit headers (X-RateLimit-*)

Adım 192: Authentication/Authorization ekle (JWT)
  - JWT token oluşturma
  - JWT token doğrulama
  - Refresh token mekanizması
  - Token expiration
  - Role-based access control (RBAC)
  - API key desteği (opsiyonel)

Adım 193: API dokümantasyonu yaz
  - OpenAPI 3.0 şeması
  - Swagger UI entegrasyonu
  - Her endpoint için açıklama
  - Request/response örnekleri
  - Hata kodları dokümantasyonu
  - Authentication rehberi
  - Rate limiting bilgisi

Adım 194: API testleri yaz
  - Her endpoint için unit test
  - CRUD testleri
  - Authentication testleri
  - Authorization testleri
  - Validation testleri
  - Error handling testleri
  - Pagination testleri
  - Filtering testleri

Adım 195: API performans testi yap
  - Response time ölçümü
  - Throughput testi
  - Load testi (100 concurrent user)
  - Stress testi
  - Memory leak testi
  - Database connection pool testi

Adım 196: API güvenlik testi yap
  - SQL injection testi
  - XSS testi
  - CSRF testi
  - Authentication bypass testi
  - Authorization bypass testi
  - Rate limiting bypass testi
  - Input validation testi

Adım 197: API versiyonlama sistemi kur
  - URL-based versioning (/api/v1/, /api/v2/)
  - Header-based versioning
  - Deprecation policy
  - Version migration guide
  - Backward compatibility

Adım 198: API caching sistemi kur
  - Response caching
  - Cache invalidation
  - Cache TTL
  - ETag support
  - Conditional requests (If-Modified-Since)
  - Cache-Control headers

Adım 199: API logging sistemi kur
  - Request/response logging
  - Performance logging
  - Error logging
  - Access log
  - Audit log
  - Log rotation

Adım 200: API monitoring sistemi kur
  - Uptime monitoring
  - Response time tracking
  - Error rate tracking
  - Usage statistics
  - Alert kuralları
  - Health check endpoint

================================================================================
# FAZ 2: WEB ARAYÜZÜ (LAİN TEMALİ) (Adım 201-500)
================================================================================

## A. Tasarım Sistemi - Lain Teması (Adım 201-250)

Adım 201: Lain temasını tasarla - renk paleti
  - Primary: #0a0a12 (derin siyah-mavi, Wired'in karanlık dünyası)
  - Secondary: #1a1a2e (koyu lavi
