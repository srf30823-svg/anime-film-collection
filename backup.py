#!/usr/bin/env python3
"""
Echo v5.3 - Yedekleme Sistemi
- SQLite DB yedekleme (gzip)
- Memory/Hafıza yedekleme
- İsteğe bağlı GitHub push
"""
import sqlite3, gzip, shutil, os, sys, json, subprocess
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "data", "recommender.db")
BACKUP_DIR = os.path.join(BASE, "backups")
MEMORY_DIR = os.path.expanduser("~/.hermes")

def backup_sqlite():
    """SQLite DB'yi gzip ile yedekle."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"recommender_{ts}.db.gz")
    
    # DB'yi kopyala ve sıkıştır
    temp_copy = os.path.join(BACKUP_DIR, f"temp_{ts}.db")
    shutil.copy2(DB_PATH, temp_copy)
    
    with open(temp_copy, "rb") as f_in:
        with gzip.open(backup_path, "wb", compresslevel=9) as f_out:
            f_out.write(f_in.read())
    
    os.remove(temp_copy)
    
    # Boyut raporu
    orig_size = os.path.getsize(DB_PATH)
    backup_size = os.path.getsize(backup_path)
    ratio = (1 - backup_size / orig_size) * 100
    print(f"✅ SQLite yedek: {backup_path}")
    print(f"   Boyut: {orig_size//1024}KB → {backup_size//1024}KB (%{ratio:.0f} sıkıştırma)")
    return backup_path

def backup_memory():
    """Hermes memory dosyalarını yedekle."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"memory_{ts}.tar.gz")
    
    # Memory dosyalarını tar.gz ile yedekle
    memory_files = []
    if os.path.exists(MEMORY_DIR):
        for f in os.listdir(MEMORY_DIR):
            if f.endswith((".json", ".yaml", ".yml", ".md", ".txt", ".db")):
                fp = os.path.join(MEMORY_DIR, f)
                if os.path.isfile(fp):
                    memory_files.append(fp)
    
    if memory_files:
        import tarfile
        with tarfile.open(backup_path, "w:gz") as tar:
            for fp in memory_files:
                tar.add(fp, arcname=os.path.basename(fp))
        print(f"✅ Memory yedek: {backup_path} ({len(memory_files)} dosya)")
    else:
        print("⚠️ Memory dizini bulunamadı veya boş")
    
    return backup_path

def cleanup_old_backups(keep=30):
    """Eski yedekleri temizle."""
    if not os.path.exists(BACKUP_DIR):
        return
    
    backups = []
    for f in os.listdir(BACKUP_DIR):
        fp = os.path.join(BACKUP_DIR, f)
        if os.path.isfile(fp) and (f.endswith(".gz") or f.endswith(".db")):
            backups.append((os.path.getmtime(fp), fp))
    
    backups.sort(reverse=True)  # En yeni başta
    
    removed = 0
    for _, fp in backups[keep:]:
        os.remove(fp)
        removed += 1
    
    if removed:
        print(f"🗑️ {removed} eski yedek temizlendi (son {keep} tutuldu)")

def git_push():
    """GitHub'a push et (eğer git repo ise)."""
    try:
        # Değişiklik var mı kontrol et
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=BASE, capture_output=True, text=True, timeout=10
        )
        if not result.stdout.strip():
            print("ℹ️ Git değişiklik yok, push gerekmez")
            return False
        
        # Add, commit, push
        subprocess.run(["git", "add", "-A"], cwd=BASE, check=True, timeout=10)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subprocess.run(
            ["git", "commit", "-m", f"Auto backup - {ts}"],
            cwd=BASE, check=True, timeout=30
        )
        subprocess.run(["git", "push"], cwd=BASE, check=True, timeout=60)
        print(f"✅ GitHub push tamamlandı")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git push hatası: {e}")
        return False
    except FileNotFoundError:
        print("⚠️ Git kurulu değil veya PATH'de yok")
        return False

def main():
    print("=" * 50)
    print("Echo Yedekleme Sistemi v5.3")
    print(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 1. SQLite yedekle
    print("\n[1/4] SQLite DB yedekleniyor...")
    backup_sqlite()
    
    # 2. Memory yedekle
    print("\n[2/4] Memory yedekleniyor...")
    backup_memory()
    
    # 3. Eski yedekleri temizle
    print("\n[3/4] Eski yedekler temizleniyor...")
    cleanup_old_backups(keep=30)
    
    # 4. GitHub push (opsiyonel)
    print("\n[4/4] GitHub push...")
    git_push()
    
    print("\n" + "=" * 50)
    print("✅ Yedekleme tamamlandı!")
    print("=" * 50)

if __name__ == "__main__":
    main()
