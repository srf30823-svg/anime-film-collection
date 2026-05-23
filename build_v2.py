#!/usr/bin/env python3
"""OWL - Kapsamlı Anime Film Analiz Sistemi v1.0"""
import json, os, sys
from datetime import datetime

BASE = "/data/data/com.termux/files/home/anime-project"
os.makedirs(f"{BASE}/output/txt", exist_ok=True)
os.makedirs(f"{BASE}/output/stats", exist_ok=True)

# === İZLENEN FİLMLER (çıkarılacak) ===
WATCHED = set(w.strip().lower() for w in open(f"{BASE}/data/watched.txt").readlines()) if os.path.exists(f"{BASE}/data/watched.txt") else set()

# === TÜR İSİMLERİ ===
CATS = {
    "philosophical_surreal": "Felsefi&Surreal", "action_epic": "Aksiyon&Muthis",
    "psychological": "Psikolojik", "comedy_satirical": "Komedi&Satirik",
    "emotional_slice": "Duygusal&Incelikli", "fantasy_adventure": "Fantastik&Macera",
    "sci_fi": "BilimKurgu", "cyberpunk": "Cyberpunk", "mystery": "Gizem",
    "horror_thriller": "Korku&Gerilim", "romance_drama": "Romantik&Drama",
    "sports": "Spor", "historical": "Tarihi", "music_art": "Muzik&Sanat",
    "mecha": "Mekka", "short_film": "KisaFilm",
}
TASTE_W = {
    "philosophical_surreal": 10, "action_epic": 9, "psychological": 9,
    "cyberpunk": 9, "comedy_satirical": 8, "emotional_slice": 8,
    "fantasy_adventure": 8, "music_art": 7, "sci_fi": 7, "sports": 7,
    "mystery": 7, "short_film": 7, "historical": 6, "horror_thriller": 6,
    "mecha": 6, "romance_drama": 5,
}

# === FİLM VERİTABANI ===
FILMS = [
    # --- 1960-1980 ---
    {"title":"The Little Prince and the Eight-Headed Dragon","year":1963,"director":"Yugo Serikawa","categories":["fantasy_adventure"],"mal_score":6.5,"imdb_score":6.2},
    {"title":"Hols: Prince of the Sun","year":1968,"director":"Isao Takahata","categories":["fantasy_adventure","action_epic"],"mal_score":7.5,"imdb_score":7.2},
    {"title":"The Wonderful World of Puss 'n Boots","year":1969,"director":"Kimio Yabuki","categories":["fantasy_adventure","comedy_satirical"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"Cleopatra","year":1970,"director":"Eiichi Yamamoto","categories":["historical","fantasy_adventure"],"mal_score":6.2,"imdb_score":5.9},
    {"title":"Belladonna of Sadness","year":1973,"director":"Eiichi Yamamoto","categories":["philosophical_surreal","historical","horror_thriller"],"mal_score":7.5,"imdb_score":7.3},
    {"title":"Space Battleship Yamato","year":1977,"director":"Toshio Masuda","categories":["sci_fi","action_epic"],"mal_score":7.5,"imdb_score":7.2},
    {"title":"Lupin III: The Castle of Cagliostro","year":1979,"director":"Hayao Miyazaki","categories":["action_epic","fantasy_adventure"],"mal_score":7.8,"imdb_score":7.6},
    {"title":"Galaxy Express 999","year":1979,"director":"Rintaro","categories":["sci_fi","fantasy_adventure"],"mal_score":7.5,"imdb_score":7.2},
    {"title":"Adieu Galaxy Express 999","year":1981,"director":"Rintaro","categories":["sci_fi","emotional_slice"],"mal_score":7.2,"imdb_score":6.9},
    {"title":"Arcadia of My Youth","year":1982,"director":"Tomoharu Katsumata","categories":["sci_fi","action_epic"],"mal_score":7.3,"imdb_score":7.0},

    # --- 1980-1990 ---
    {"title":"Phoenix 2772","year":1980,"director":"Sugii Gisaburo","categories":["sci_fi","romance_drama"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"Doraemon: Nobita's Little Star Wars","year":1985,"director":"Tsutomu Shibayama","categories":["sci_fi","comedy_satirical"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"Nausicaa of the Valley of the Wind","year":1984,"director":"Hayao Miyazaki","categories":["fantasy_adventure","sci_fi","emotional_slice"],"mal_score":8.33,"imdb_score":8.0},
    {"title":"Castle in the Sky","year":1986,"director":"Hayao Miyazaki","categories":["fantasy_adventure","action_epic"],"mal_score":8.18,"imdb_score":8.0},
    {"title":"My Neighbor Totoro","year":1988,"director":"Hayao Miyazaki","categories":["emotional_slice","fantasy_adventure"],"mal_score":8.25,"imdb_score":8.1},
    {"title":"Kikis Delivery Service","year":1989,"director":"Hayao Miyazaki","categories":["fantasy_adventure","emotional_slice"],"mal_score":8.18,"imdb_score":7.8},
    {"title":"Grave of the Fireflies","year":1988,"director":"Isao Takahata","categories":["emotional_slice","historical"],"mal_score":8.5,"imdb_score":8.5},
    {"title":"Akira","year":1988,"director":"Katsuhiro Otomo","categories":["cyberpunk","sci_fi","action_epic","philosophical_surreal"],"mal_score":8.15,"imdb_score":8.0},
    {"title":"Urusei Yatsura 2: Beautiful Dreamer","year":1984,"director":"Mamoru Oshii","categories":["philosophical_surreal","comedy_satirical"],"mal_score":7.55,"imdb_score":7.4},
    {"title":"Angel's Egg","year":1985,"director":"Mamoru Oshii","categories":["philosophical_surreal","emotional_slice"],"mal_score":7.45,"imdb_score":7.3},
    {"title":"Patlabor: The Movie","year":1989,"director":"Mamoru Oshii","categories":["mecha","sci_fi","action_epic"],"mal_score":7.58,"imdb_score":7.1},
    {"title":"Mobile Suit Gundam: Char's Counterattack","year":1988,"director":"Yoshiyuki Tomino","categories":["mecha","sci_fi","action_epic"],"mal_score":7.8,"imdb_score":7.5},
    {"title":"Vampire Hunter D","year":1985,"director":"Toyoo Ashida","categories":["horror_thriller","fantasy_adventure"],"mal_score":7.2,"imdb_score":6.9},
    {"title":"Wicked City","year":1987,"director":"Yoshiaki Kawajiri","categories":["horror_thriller","action_epic","cyberpunk"],"mal_score":7.0,"imdb_score":6.7},
    {"title":"Demon City Shinjuku","year":1988,"director":"Yoshiaki Kawajiri","categories":["horror_thriller","action_epic","cyberpunk"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"The Five Star Stories","year":1989,"director":"Kazuo Yamazaki","categories":["sci_fi","action_epic","mecha"],"mal_score":6.5,"imdb_score":6.2},
    {"title":"Tailender","year":1988,"director":"Tetsuro Imazawa","categories":["sci_fi","action_epic"],"mal_score":5.8,"imdb_score":5.5},

    # --- 1990-2000 ---
    {"title":"Only Yesterday","year":1991,"director":"Isao Takahata","categories":["emotional_slice","romance_drama"],"mal_score":7.94,"imdb_score":7.6},
    {"title":"Pom Poko","year":1994,"director":"Isao Takahata","categories":["fantasy_adventure","comedy_satirical"],"mal_score":7.1,"imdb_score":7.3},
    {"title":"Whisper of the Heart","year":1995,"director":"Yoshifumi Kondo","categories":["romance_drama","emotional_slice"],"mal_score":8.22,"imdb_score":7.8},
    {"title":"The Cat Returns","year":2002,"director":"Hiroyuki Morita","categories":["fantasy_adventure","comedy_satirical"],"mal_score":7.53,"imdb_score":7.2},
    {"title":"Princess Mononoke","year":1997,"director":"Hayao Miyazaki","categories":["fantasy_adventure","action_epic","historical"],"mal_score":8.66,"imdb_score":8.3},
    {"title":"Ocean Waves","year":1993,"director":"Tomomi Mochizuki","categories":["romance_drama","emotional_slice"],"mal_score":6.89,"imdb_score":6.8},
    {"title":"My Neighbors the Yamadas","year":1999,"director":"Isao Takahata","categories":["comedy_satirical","emotional_slice"],"mal_score":7.33,"imdb_score":7.1},
    {"title":"Perfect Blue","year":1997,"director":"Satoshi Kon","categories":["psychological","horror_thriller","philosophical_surreal"],"mal_score":8.54,"imdb_score":8.0},
    {"title":"Ghost in the Shell","year":1995,"director":"Mamoru Oshii","categories":["cyberpunk","sci_fi","philosophical_surreal","action_epic"],"mal_score":8.27,"imdb_score":7.9},
    {"title":"Ghost in the Shell 2: Innocence","year":2004,"director":"Mamoru Oshii","categories":["cyberpunk","philosophical_surreal","sci_fi"],"mal_score":7.63,"imdb_score":7.4},
    {"title":"Patlabor 2: The Movie","year":1993,"director":"Mamoru Oshii","categories":["mecha","sci_fi","philosophical_surreal"],"mal_score":7.72,"imdb_score":7.3},
    {"title":"Jin-Roh: The Wolf Brigade","year":1999,"director":"Hiroyuki Okiura","categories":["action_epic","philosophical_surreal","historical"],"mal_score":7.6,"imdb_score":7.3},
    {"title":"Ninja Scroll","year":1993,"director":"Yoshiaki Kawajiri","categories":["action_epic","historical","horror_thriller"],"mal_score":7.5,"imdb_score":7.4},
    {"title":"Vampire Hunter D: Bloodlust","year":2000,"director":"Yoshiaki Kawajiri","categories":["horror_thriller","action_epic","fantasy_adventure"],"mal_score":7.6,"imdb_score":7.4},
    {"title":"Cardcaptor Sakura: The Movie","year":1999,"director":"Morio Asaka","categories":["fantasy_adventure","romance_drama"],"mal_score":7.8,"imdb_score":7.4},
    {"title":"Cardcaptor Sakura Movie 2: The Sealed Card","year":2000,"director":"Morio Asaka","categories":["fantasy_adventure","romance_drama"],"mal_score":8.0,"imdb_score":7.6},
    {"title":"Revolutionary Girl Utena: Adolescence of Utena","year":1999,"director":"Kunihiko Ikuhara","categories":["philosophical_surreal","psychological","romance_drama"],"mal_score":7.8,"imdb_score":7.4},
    {"title":"Love Hina Again","year":2002,"director":"Yoshiaki Iwasaki","categories":["comedy_satirical","romance_drama"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"Rurouni Kenshin: Trust and Betrayal","year":1999,"director":"Kazuhiro Furuhashi","categories":["action_epic","historical","emotional_slice"],"mal_score":8.7,"imdb_score":8.3},
    {"title":"The Vision of Escaflowne","year":2000,"director":"Kazuki Akane","categories":["fantasy_adventure","mecha","romance_drama"],"mal_score":7.3,"imdb_score":7.0},
    {"title":"Record of Lodoss War: Chronicles of the Heroic Knight","year":1998,"director":"Kunihiko Yuyama","categories":["fantasy_adventure","action_epic"],"mal_score":7.0,"imdb_score":6.7},
    {"title":"Legend of the Galactic Heroes: My Conquest is the Sea of Stars","year":1988,"director":"Noboru Ishiguro","categories":["sci_fi","historical","action_epic"],"mal_score":7.2,"imdb_score":6.9},
    {"title":"Spriggan","year":1998,"director":"Masahiko Murata","categories":["action_epic","sci_fi"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"X/1999","year":1996,"director":"Rintaro","categories":["action_epic","fantasy_adventure","horror_thriller"],"mal_score":7.2,"imdb_score":6.8},
    {"title":"Blood: The Last Vampire","year":2000,"director":"Hiroyuki Kitakubo","categories":["horror_thriller","action_epic"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"The Laws of the Sun","year":2000,"director":"Takaaki Ishiyama","categories":["sci_fi","fantasy_adventure"],"mal_score":5.5,"imdb_score":5.2},

    # --- 2000-2010 ---
    {"title":"Millennium Actress","year":2001,"director":"Satoshi Kon","categories":["philosophical_surreal","emotional_slice","romance_drama"],"mal_score":8.17,"imdb_score":7.8},
    {"title":"Tokyo Godfathers","year":2003,"director":"Satoshi Kon","categories":["comedy_satirical","emotional_slice"],"mal_score":8.1,"imdb_score":7.8},
    {"title":"Paprika","year":2006,"director":"Satoshi Kon","categories":["philosophical_surreal","sci_fi","psychological"],"mal_score":8.04,"imdb_score":7.7},
    {"title":"Spirited Away","year":2001,"director":"Hayao Miyazaki","categories":["fantasy_adventure","emotional_slice"],"mal_score":8.77,"imdb_score":8.6},
    {"title":"Howls Moving Castle","year":2004,"director":"Hayao Miyazaki","categories":["fantasy_adventure","romance_drama"],"mal_score":8.58,"imdb_score":8.2},
    {"title":"Tales from Earthsea","year":2006,"director":"Goro Miyazaki","categories":["fantasy_adventure"],"mal_score":6.53,"imdb_score":6.4},
    {"title":"Ponyo","year":2008,"director":"Hayao Miyazaki","categories":["fantasy_adventure","emotional_slice"],"mal_score":7.89,"imdb_score":7.6},
    {"title":"The Place Promised in Our Early Days","year":2004,"director":"Makoto Shinkai","categories":["sci_fi","romance_drama","emotional_slice"],"mal_score":7.02,"imdb_score":6.9},
    {"title":"5 Centimeters Per Second","year":2007,"director":"Makoto Shinkai","categories":["romance_drama","emotional_slice"],"mal_score":7.56,"imdb_score":7.5},
    {"title":"Voices of a Distant Star","year":2002,"director":"Makoto Shinkai","categories":["sci_fi","romance_drama","emotional_slice"],"mal_score":7.18,"imdb_score":7.2},
    {"title":"The Girl Who Leapt Through Time","year":2006,"director":"Mamoru Hosoda","categories":["sci_fi","romance_drama","emotional_slice"],"mal_score":8.1,"imdb_score":7.7},
    {"title":"Summer Wars","year":2009,"director":"Mamoru Hosoda","categories":["sci_fi","comedy_satirical","emotional_slice"],"mal_score":7.9,"imdb_score":7.5},
    {"title":"Tekkonkinkreet","year":2006,"director":"Michael Arias","categories":["action_epic","philosophical_surreal","emotional_slice"],"mal_score":7.8,"imdb_score":7.4},
    {"title":"Mind Game","year":2004,"director":"Masaaki Yuasa","categories":["philosophical_surreal","comedy_satirical","psychological"],"mal_score":7.85,"imdb_score":7.6},
    {"title":"Redline","year":2009,"director":"Takeshi Koike","categories":["action_epic","sci_fi","comedy_satirical"],"mal_score":8.2,"imdb_score":7.7},
    {"title":"Metropolis","year":2001,"director":"Rintaro","categories":["sci_fi","philosophical_surreal"],"mal_score":7.2,"imdb_score":7.0},
    {"title":"Steamboy","year":2004,"director":"Katsuhiro Otomo","categories":["sci_fi","action_epic","historical"],"mal_score":7.02,"imdb_score":6.8},
    {"title":"Cowboy Bebop: The Movie","year":2001,"director":"Shinichiro Watanabe","categories":["action_epic","sci_fi","cyberpunk"],"mal_score":8.0,"imdb_score":7.6},
    {"title":"Fullmetal Alchemist: The Sacred Star of Milos","year":2011,"director":"Kazuya Murata","categories":["action_epic","fantasy_adventure"],"mal_score":7.5,"imdb_score":7.1},
    {"title":"Sword of the Stranger","year":2007,"director":"Masahiro Ando","categories":["action_epic","historical"],"mal_score":8.1,"imdb_score":7.7},
    {"title":"Colourful","year":2010,"director":"Keiichi Hara","categories":["emotional_slice","philosophical_surreal"],"mal_score":7.6,"imdb_score":7.3},
    {"title":"Colorful","year":2010,"director":"Keiichi Hara","categories":["emotional_slice","philosophical_surreal"],"mal_score":7.6,"imdb_score":7.3},
    {"title":"Summer Days with Coo","year":2007,"director":"Keiichi Hara","categories":["fantasy_adventure","emotional_slice","comedy_satirical"],"mal_score":7.4,"imdb_score":7.1},
    {"title":"The Sky Crawlers","year":2008,"director":"Mamoru Oshii","categories":["sci_fi","philosophical_surreal","action_epic"],"mal_score":7.15,"imdb_score":6.8},
    {"title":"Dead Leaves","year":2004,"director":"Hiroyuki Imaishi","categories":["comedy_satirical","sci_fi","action_epic"],"mal_score":7.1,"imdb_score":6.8},
    {"title":"Samurai Champloo: The Movie","year":2007,"director":"Shinichiro Watanabe","categories":["action_epic","historical"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"Rosario + Vampire CAPU2","year":2008,"director":"Takayuki Inagaki","categories":["comedy_satirical","horror_thriller"],"mal_score":6.2,"imdb_score":5.9},

    # --- 2010-2015 ---
    {"title":"Wolf Children","year":2012,"director":"Mamoru Hosoda","categories":["fantasy_adventure","emotional_slice","romance_drama"],"mal_score":8.55,"imdb_score":8.2},
    {"title":"From Up on Poppy Hill","year":2011,"director":"Goro Miyazaki","categories":["romance_drama","emotional_slice","historical"],"mal_score":7.44,"imdb_score":7.4},
    {"title":"The Wind Rises","year":2013,"director":"Hayao Miyazaki","categories":["historical","romance_drama","emotional_slice"],"mal_score":7.96,"imdb_score":7.8},
    {"title":"The Tale of The Princess Kaguya","year":2013,"director":"Isao Takahata","categories":["fantasy_adventure","emotional_slice","historical"],"mal_score":8.1,"imdb_score":8.0},
    {"title":"K-On! The Movie","year":2011,"director":"Naoko Yamada","categories":["music_art","comedy_satirical","emotional_slice"],"mal_score":7.9,"imdb_score":7.5},
    {"title":"A Silent Voice","year":2016,"director":"Naoko Yamada","categories":["emotional_slice","romance_drama"],"mal_score":8.9,"imdb_score":8.2},
    {"title":"The Tatami Galaxy","year":2010,"director":"Masaaki Yuasa","categories":["philosophical_surreal","psychological","comedy_satirical"],"mal_score":8.45,"imdb_score":8.1},
    {"title":"Children Who Chase Lost Voices","year":2011,"director":"Makoto Shinkai","categories":["fantasy_adventure","emotional_slice"],"mal_score":7.33,"imdb_score":7.1},
    {"title":"The Garden of Words","year":2013,"director":"Makoto Shinkai","categories":["romance_drama","emotional_slice"],"mal_score":7.48,"imdb_score":7.4},
    {"title":"Maquia: When the Promised Flower Blooms","year":2018,"director":"Mari Okada","categories":["fantasy_adventure","emotional_slice","romance_drama"],"mal_score":8.05,"imdb_score":7.6},
    {"title":"In This Corner of the World","year":2016,"director":"Sunao Katabuchi","categories":["historical","emotional_slice","romance_drama"],"mal_score":8.15,"imdb_score":7.8},
    {"title":"Anthem of the Heart","year":2015,"director":"Mari Okada","categories":["emotional_slice","romance_drama","music_art"],"mal_score":7.8,"imdb_score":7.4},
    {"title":"Her Blue Sky","year":2019,"director":"Mari Okada","categories":["romance_drama","emotional_slice","fantasy_adventure"],"mal_score":7.5,"imdb_score":7.2},
    {"title":"Miss Hokusai","year":2015,"director":"Keiichi Hara","categories":["historical","emotional_slice","music_art"],"mal_score":7.5,"imdb_score":7.2},
    {"title":"The Boy and the Beast","year":2015,"director":"Mamoru Hosoda","categories":["fantasy_adventure","action_epic","emotional_slice"],"mal_score":7.7,"imdb_score":7.3},
    {"title":"Psycho-Pass: The Movie","year":2015,"director":"Naoyoshi Shiotani","categories":["sci_fi","psychological","philosophical_surreal"],"mal_score":7.5,"imdb_score":7.1},
    {"title":"Attack on Titan: Chronicle","year":2020,"director":"Tetsuro Araki","categories":["action_epic","fantasy_adventure","philosophical_surreal"],"mal_score":8.5,"imdb_score":8.0},
    {"title":"The Anthem of the Heart","year":2015,"director":"Mari Okada","categories":["emotional_slice","romance_drama","music_art"],"mal_score":7.8,"imdb_score":7.4},
    {"title":"Mai Mai Miracle","year":2009,"director":"Sunao Katabuchi","categories":["emotional_slice","historical","fantasy_adventure"],"mal_score":7.3,"imdb_score":7.0},
    {"title":"Birthday Wonderland","year":2019,"director":"Keiichi Hara","categories":["fantasy_adventure","emotional_slice"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"Mary and the Witchs Flower","year":2017,"director":"Hiromasa Yonebayashi","categories":["fantasy_adventure","emotional_slice"],"mal_score":7.1,"imdb_score":6.8},
    {"title":"Mirai","year":2018,"director":"Mamoru Hosoda","categories":["fantasy_adventure","emotional_slice"],"mal_score":7.3,"imdb_score":7.0},
    {"title":"Modest Heroes","year":2018,"director":"Studio Ponoc","categories":["emotional_slice","short_film"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"Wreck-It Ralph","year":2012,"director":"Rich Moore","categories":["comedy_satirical","action_epic"],"mal_score":7.5,"imdb_score":7.1},

    # --- 2015-2020 ---
    {"title":"The Night Is Short, Walk on Girl","year":2017,"director":"Masaaki Yuasa","categories":["comedy_satirical","romance_drama","philosophical_surreal"],"mal_score":8.05,"imdb_score":7.6},
    {"title":"Lu Over the Wall","year":2017,"director":"Masaaki Yuasa","categories":["fantasy_adventure","emotional_slice"],"mal_score":7.1,"imdb_score":6.8},
    {"title":"Ride Your Wave","year":2019,"director":"Masaaki Yuasa","categories":["romance_drama","emotional_slice","fantasy_adventure"],"mal_score":7.45,"imdb_score":7.0},
    {"title":"Liz and the Blue Bird","year":2018,"director":"Naoko Yamada","categories":["emotional_slice","music_art","romance_drama"],"mal_score":8.1,"imdb_score":7.6},
    {"title":"Violet Evergarden: The Movie","year":2020,"director":"Taichi Ishidate","categories":["emotional_slice","romance_drama"],"mal_score":8.5,"imdb_score":8.1},
    {"title":"Promare","year":2019,"director":"Hiroyuki Imaishi","categories":["action_epic","sci_fi","comedy_satirical"],"mal_score":7.8,"imdb_score":7.1},
    {"title":"Ride Your Wave","year":2019,"director":"Masaaki Yuasa","categories":["romance_drama","emotional_slice"],"mal_score":7.45,"imdb_score":7.0},
    {"title":"Children of the Sea","year":2019,"director":"Ayumu Watanabe","categories":["philosophical_surreal","fantasy_adventure","emotional_slice"],"mal_score":7.1,"imdb_score":6.8},
    {"title":"Weathering with You","year":2019,"director":"Makoto Shinkai","categories":["romance_drama","fantasy_adventure","emotional_slice"],"mal_score":8.26,"imdb_score":7.5},
    {"title":"The First Slam Dunk","year":2022,"director":"Takehiko Inoue","categories":["sports","emotional_slice","action_epic"],"mal_score":8.5,"imdb_score":8.0},

    # --- 2020-2026 ---
    {"title":"Jujutsu Kaisen 0","year":2021,"director":"Seong-Hu Park","categories":["action_epic","fantasy_adventure"],"mal_score":8.5,"imdb_score":7.8},
    {"title":"One Piece Film: Red","year":2022,"director":"Goro Taniguchi","categories":["action_epic","music_art","fantasy_adventure"],"mal_score":7.5,"imdb_score":7.0},
    {"title":"Suzume","year":2022,"director":"Makoto Shinkai","categories":["fantasy_adventure","emotional_slice","action_epic"],"mal_score":8.35,"imdb_score":7.6},
    {"title":"Belle","year":2021,"director":"Mamoru Hosoda","categories":["fantasy_adventure","music_art","emotional_slice"],"mal_score":7.65,"imdb_score":7.2},
    {"title":"Inu-Oh","year":2021,"director":"Masaaki Yuasa","categories":["music_art","historical","philosophical_surreal"],"mal_score":7.6,"imdb_score":7.2},
    {"title":"The Boy and the Heron","year":2023,"director":"Hayao Miyazaki","categories":["fantasy_adventure","philosophical_surreal","emotional_slice"],"mal_score":7.66,"imdb_score":7.4},
    {"title":"Spy x Family Code: White","year":2023,"director":"Takashi Katagiri","categories":["action_epic","comedy_satirical"],"mal_score":7.5,"imdb_score":7.0},
    {"title":"Digimon Adventure: Last Evolution Kizuna","year":2020,"director":"Tomohisa Taguchi","categories":["action_epic","emotional_slice"],"mal_score":7.8,"imdb_score":7.4},
    {"title":"Ranking of Kings: The Treasure Chest of Courage","year":2023,"year":2023,"director":"Shingo Kaneko","categories":["fantasy_adventure","emotional_slice"],"mal_score":7.2,"imdb_score":6.8},
    {"title":"Chainsaw Man: Reze Arc","year":2025,"director":"Tatsuya Yoshihara","categories":["action_epic","horror_thriller"],"mal_score":9.13,"imdb_score":8.5},
    {"title":"Mononoke the Movie: Phantom in the Rain","year":2024,"director":"Kenji Nakamura","categories":["horror_thriller","philosophical_surreal","historical"],"mal_score":7.8,"imdb_score":7.5},
    {"title":"The Colors Within","year":2024,"director":"Naoko Yamada","categories":["emotional_slice","music_art"],"mal_score":7.7,"imdb_score":7.3},
    {"title":"Sailor Moon Cosmos Part 1","year":2024,"director":"Kazuko Tadano","categories":["fantasy_adventure","romance_drama"],"mal_score":7.5,"imdb_score":7.0},
    {"title":"Sailor Moon Cosmos Part 2","year":2024,"director":"Kazuko Tadano","categories":["fantasy_adventure","romance_drama"],"mal_score":7.5,"imdb_score":7.0},
    {"title":"Look Back","year":2024,"director":"Kiyotaka Oshiyama","categories":["emotional_slice","short_film"],"mal_score":8.5,"imdb_score":8.0},
    {"title":"Totto-chan: The Little Girl at the Window","year":2023,"director":"Shinnosuke Yakuwa","categories":["emotional_slice","historical"],"mal_score":7.2,"imdb_score":6.8},
    {"title":"The Imaginary","year":2023,"director":"Yoshiyuki Momose","categories":["fantasy_adventure","emotional_slice"],"mal_score":7.5,"imdb_score":7.1},
    {"title":"Nimona","year":2023,"director":"Nick Bruno","categories":["action_epic","comedy_satirical"],"mal_score":7.8,"imdb_score":7.3},

    # --- EKSTRA FİLMLER (genişletilmiş liste) ---
    {"title":"Appleseed","year":2004,"director":"Shinji Aramaki","categories":["sci_fi","cyberpunk","action_epic"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"Appleseed: Ex Machina","year":2007,"director":"Shinji Aramaki","categories":["sci_fi","cyberpunk"],"mal_score":6.5,"imdb_score":6.2},
    {"title":"Appleseed Alpha","year":2014,"director":"Shinji Aramaki","categories":["sci_fi","cyberpunk"],"mal_score":6.2,"imdb_score":5.9},
    {"title":"Blade Runner: Black Out 2022","year":2017,"director":"Shinichiro Watanabe","categories":["sci_fi","cyberpunk"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"Burn the Witch","year":2020,"director":"Tatsuro Koishi","categories":["action_epic","fantasy_adventure"],"mal_score":6.5,"imdb_score":6.2},
    {"title":"Dragon Ball Z: Broly – The Legendary Super Saiyan","year":1993,"director":"Shigeyasu Yamauchi","categories":["action_epic"],"mal_score":7.2,"imdb_score":6.9},
    {"title":"Dragon Ball Z: Broly – Second Coming","year":1994,"director":"Shigeyasu Yamauchi","categories":["action_epic"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"Dragon Ball Z: Bio-Broly","year":1994,"director":"Yoshihiro Ueda","categories":["action_epic"],"mal_score":6.2,"imdb_score":5.9},
    {"title":"Dragon Ball Z: Fusion Reborn","year":1995,"director":"Shigeyasu Yamauchi","categories":["action_epic"],"mal_score":7.0,"imdb_score":6.7},
    {"title":"Dragon Ball Z: Wrath of the Dragon","year":1995,"director":"Mitsuo Hashimoto","categories":["action_epic"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"Dragon Ball Z: Battle of Gods","year":2013,"director":"Masahiro Hosoda","categories":["action_epic","comedy_satirical"],"mal_score":7.4,"imdb_score":7.0},
    {"title":"Dragon Ball Z: Resurrection F","year":2015,"director":"Tadayoshi Yamamuro","categories":["action_epic"],"mal_score":7.2,"imdb_score":6.8},
    {"title":"Dragon Ball Super: Broly","year":2018,"director":"Tadayoshi Yamamuro","categories":["action_epic"],"mal_score":8.1,"imdb_score":7.8},
    {"title":"Dragon Ball Super: Super Hero","year":2022,"director":"Tadayoshi Yamamuro","categories":["action_epic","comedy_satirical"],"mal_score":7.5,"imdb_score":7.1},
    {"title":"Oban Star-Racers","year":2006,"director":"Savin Yeatman-Eiffel","categories":["sci_fi","action_epic","sports"],"mal_score":7.2,"imdb_score":6.9},
    {"title":"Kingsglaive: Final Fantasy XV","year":2016,"director":"Takeshi Nozue","categories":["action_epic","fantasy_adventure"],"mal_score":7.0,"imdb_score":6.7},
    {"title":"Kingsglaive: Final Fantasy XV","year":2016,"director":"Takeshi Nozue","categories":["action_epic","fantasy_adventure"],"mal_score":7.0,"imdb_score":6.7},
    {"title":"Final Fantasy VII: Advent Children","year":2005,"director":"Tetsuya Nomura","categories":["action_epic","sci_fi"],"mal_score":7.2,"imdb_score":6.9},
    {"title":"Space Pirate Captain Harlock","year":2013,"director":"Shinji Aramaki","categories":["sci_fi","action_epic"],"mal_score":6.5,"imdb_score":6.2},
    {"title":"Gantz:O","year":2016,"director":"Yasushi Kawamura","categories":["action_epic","sci_fi","horror_thriller"],"mal_score":7.2,"imdb_score":6.9},
    {"title":"Inuyasha: Affections Touching Across Time","year":2001,"director":"Toshiya Shinohara","categories":["action_epic","fantasy_adventure","romance_drama"],"mal_score":7.2,"imdb_score":6.9},
    {"title":"Inuyasha: The Castle Beyond the Looking Glass","year":2002,"director":"Toshiya Shinohara","categories":["action_epic","fantasy_adventure"],"mal_score":7.3,"imdb_score":7.0},
    {"title":"Inuyasha: Swords of an Honorable Ruler","year":2003,"director":"Toshiya Shinohara","categories":["action_epic","fantasy_adventure"],"mal_score":7.4,"imdb_score":7.1},
    {"title":"Inuyasha: Fire on the Mystic Island","year":2004,"director":"Toshiya Shinohara","categories":["action_epic","fantasy_adventure"],"mal_score":7.0,"imdb_score":6.7},
    {"title":"In This Corner of the World: Sincerely Yours","year":2019,"director":"Sunao Katabuchi","categories":["historical","emotional_slice"],"mal_score":7.2,"imdb_score":6.8},
    {"title":"The Kingdom of Dreams and Madness","year":2013,"director":"Mami Sunada","categories":["music_art","emotional_slice"],"mal_score":7.5,"imdb_score":7.2},
    {"title":"The Tale of the Princess Kaguya","year":2013,"director":"Isao Takahata","categories":["fantasy_adventure","emotional_slice","historical"],"mal_score":8.1,"imdb_score":8.0},
    {"title":"Only Yesterday","year":1991,"director":"Isao Takahata","categories":["emotional_slice","romance_drama"],"mal_score":7.94,"imdb_score":7.6},
    {"title":"Pom Poko","year":1994,"director":"Isao Takahata","categories":["fantasy_adventure","comedy_satirical"],"mal_score":7.1,"imdb_score":7.3},
    {"title":"My Neighbors the Yamadas","year":1999,"director":"Isao Takahata","categories":["comedy_satirical","emotional_slice"],"mal_score":7.33,"imdb_score":7.1},
    {"title":"The Red Turtle","year":2016,"director":"Michael Dudok de Wit","categories":["emotional_slice","fantasy_adventure","short_film"],"mal_score":7.5,"imdb_score":7.2},
    {"title":"The Red Spectacles","year":1987,"director":"Mamoru Oshii","categories":["philosophical_surreal","action_epic"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"StrayDog: Kerberos Panzer Cops","year":1991,"director":"Mamoru Oshii","categories":["action_epic","sci_fi"],"mal_score":7.1,"imdb_score":6.8},
    {"title":"Talking Head","year":1992,"director":"Mamoru Oshii","categories":["mystery","philosophical_surreal"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"Avalon","year":2001,"director":"Mamoru Oshii","categories":["sci_fi","cyberpunk","philosophical_surreal"],"mal_score":6.95,"imdb_score":6.5},
    {"title":"Tachigui: The Amazing Lives of the Fast Food Grifters","year":2006,"director":"Mamoru Oshii","categories":["comedy_satirical","philosophical_surreal"],"mal_score":6.5,"imdb_score":6.2},
    {"title":"Shin Godzilla","year":2016,"director":"Hideaki Anno","categories":["sci_fi","action_epic"],"mal_score":7.8,"imdb_score":7.1},
    {"title":"Shin Ultraman","year":2022,"director":"Hideaki Anno","categories":["sci_fi","action_epic"],"mal_score":7.5,"imdb_score":6.8},
    {"title":"Shin Kamen Rider","year":2023,"director":"Hideaki Anno","categories":["action_epic","sci_fi"],"mal_score":7.2,"imdb_score":6.5},
    {"title":"Garden of Sinners: Overlooking View","year":2007,"director":"Eiichi Takahashi","categories":["mystery","horror_thriller","philosophical_surreal"],"mal_score":7.5,"imdb_score":7.1},
    {"title":"Garden of Sinners: Remaining Sense of Pain","year":2008,"director":"Takahiro Miura","categories":["mystery","horror_thriller"],"mal_score":7.4,"imdb_score":7.0},
    {"title":"Garden of Sinners: The Hollow Shrine","year":2008,"director":"Takahiro Miura","categories":["mystery","philosophical_surreal"],"mal_score":7.3,"imdb_score":6.9},
    {"title":"Garden of Sinners: Paradox Spiral","year":2008,"director":"Shinsuke Takizawa","categories":["mystery","horror_thriller","philosophical_surreal"],"mal_score":7.6,"imdb_score":7.2},
    {"title":"Garden of Sinners: The Hollow Garden","year":2008,"director":"Takahiro Miura","categories":["mystery","philosophical_surreal"],"mal_score":7.2,"imdb_score":6.8},
    {"title":"Fate/stay night: Heaven's Feel I. presage flower","year":2017,"director":"Tomonori Sudo","categories":["action_epic","fantasy_adventure","romance_drama"],"mal_score":8.0,"imdb_score":7.5},
    {"title":"Fate/stay night: Heaven's Feel II. lost butterfly","year":2019,"director":"Tomonori Sudo","categories":["action_epic","fantasy_adventure","romance_drama"],"mal_score":8.2,"imdb_score":7.7},
    {"title":"Fate/stay night: Heaven's Feel III. spring song","year":2020,"director":"Tomonori Sudo","categories":["action_epic","fantasy_adventure","romance_drama"],"mal_score":8.3,"imdb_score":7.8},
    {"title":"Demon Slayer: Mugen Train","year":2020,"director":"Haruo Sotozaki","categories":["action_epic","fantasy_adventure","emotional_slice"],"mal_score":8.5,"imdb_score":8.2},
    {"title":"Demon Slayer: To the Swordsmith Village","year":2023,"director":"Haruo Sotozaki","categories":["action_epic","fantasy_adventure"],"mal_score":7.2,"imdb_score":6.8},
    {"title":"Demon Slayer: To the Hashira Training","year":2024,"director":"Haruo Sotozaki","categories":["action_epic","fantasy_adventure"],"mal_score":7.0,"imdb_score":6.5},
    {"title":"One Piece Film: Strong World","year":2009,"director":"Munehisa Sakai","categories":["action_epic","fantasy_adventure"],"mal_score":7.5,"imdb_score":7.1},
    {"title":"One Piece Film: Gold","year":2016,"director":"Hiroaki Miyamoto","categories":["action_epic","fantasy_adventure"],"mal_score":7.4,"imdb_score":7.0},
    {"title":"One Piece: Stampede","year":2019,"director":"Takashi Otsuka","categories":["action_epic","fantasy_adventure"],"mal_score":7.8,"imdb_score":7.3},
    {"title":"Sailor Moon R: The Movie","year":1993,"director":"Kunihiko Ikuhara","categories":["fantasy_adventure","romance_drama"],"mal_score":7.2,"imdb_score":6.8},
    {"title":"Sailor Moon S: The Movie","year":1994,"director":"Hiroki Shibata","categories":["fantasy_adventure","romance_drama"],"mal_score":7.0,"imdb_score":6.7},
    {"title":"Sailor Moon SuperS: The Movie","year":1995,"director":"Hiroki Shibata","categories":["fantasy_adventure","romance_drama"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"Sailor Moon Eternal Part 1","year":2021,"director":"Chiaki Kon","categories":["fantasy_adventure","romance_drama"],"mal_score":7.3,"imdb_score":6.8},
    {"title":"Sailor Moon Eternal Part 2","year":2021,"director":"Chiaki Kon","categories":["fantasy_adventure","romance_drama"],"mal_score":7.3,"imdb_score":6.8},
    {"title":"Digimon Adventure: Our War Game!","year":2000,"director":"Mamoru Hosoda","categories":["action_epic","sci_fi"],"mal_score":7.5,"imdb_score":7.1},
    {"title":"Digimon Adventure 02: Revenge of Diaboromon","year":2001,"director":"Jeff Nimoy","categories":["action_epic","sci_fi"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"Digimon Tamers: Battle of Adventurers","year":2001,"director":"Tetsuo Imazawa","categories":["action_epic","sci_fi"],"mal_score":6.7,"imdb_score":6.4},
    {"title":"Digimon Tamers: Runaway Locomon","year":2002,"director":"Tetsuo Imazawa","categories":["action_epic","sci_fi"],"mal_score":6.5,"imdb_score":6.2},
    {"title":"Digimon Frontier: Island of Lost Digimon","year":2002,"director":"Takahiro Imamura","categories":["action_epic","sci_fi"],"mal_score":6.5,"imdb_score":6.2},
    {"title":"Digimon Adventure tri. Chapter 1: Reunion","year":2015,"director":"Keitaro Motonaga","categories":["action_epic","emotional_slice"],"mal_score":7.0,"imdb_score":6.5},
    {"title":"Digimon Adventure tri. Chapter 2: Determination","year":2016,"director":"Keitaro Motonaga","categories":["action_epic","emotional_slice"],"mal_score":6.8,"imdb_score":6.3},
    {"title":"Digimon Adventure tri. Chapter 3: Confession","year":2016,"director":"Keitaro Motonaga","categories":["action_epic","emotional_slice"],"mal_score":6.7,"imdb_score":6.2},
    {"title":"Digimon Adventure tri. Chapter 4: Loss","year":2017,"director":"Keitaro Motonaga","categories":["action_epic","emotional_slice"],"mal_score":6.8,"imdb_score":6.3},
    {"title":"Digimon Adventure tri. Chapter 5: Coexistence","year":2017,"director":"Keitaro Motonaga","categories":["action_epic","emotional_slice"],"mal_score":6.7,"imdb_score":6.2},
    {"title":"Digimon Adventure tri. Chapter 6: Future","year":2018,"director":"Keitaro Motonaga","categories":["action_epic","emotional_slice"],"mal_score":7.0,"imdb_score":6.5},
    {"title":"My Hero Academia: Two Heroes","year":2018,"director":"Kenji Nagasaki","categories":["action_epic","comedy_satirical"],"mal_score":7.8,"imdb_score":7.4},
    {"title":"My Hero Academia: Heroes Rising","year":2019,"director":"Kenji Nagasaki","categories":["action_epic","emotional_slice"],"mal_score":7.9,"imdb_score":7.5},
    {"title":"My Hero Academia: World Heroes Mission","year":2021,"director":"Kenji Nagasaki","categories":["action_epic"],"mal_score":7.5,"imdb_score":7.1},
    {"title":"Sword Art Online: Ordinal Scale","year":2017,"director":"Tomohiko Ito","categories":["action_epic","sci_fi","fantasy_adventure"],"mal_score":7.2,"imdb_score":6.8},
    {"title":"Sword Art Online: Progressive - Aria of a Starless Night","year":2021,"director":"Ayako Kouno","categories":["action_epic","romance_drama","sci_fi"],"mal_score":7.5,"imdb_score":7.1},
    {"title":"Sword Art Online: Progressive - Scherzo of Deep Night","year":2022,"director":"Ayako Kouno","categories":["action_epic","romance_drama","sci_fi"],"mal_score":7.3,"imdb_score":6.9},
    {"title":"Re:Zero -Starting Life in Another World- Memory Snow","year":2018,"director":"Masaharu Watanabe","categories":["fantasy_adventure","romance_drama"],"mal_score":7.5,"imdb_score":7.0},
    {"title":"Bofuri: I Don't Want to Get Hurt, so I'll Max Out My Defense.","year":2021,"director":"Yoshitsugu Kimura","categories":["comedy_satirical","fantasy_adventure"],"mal_score":7.0,"imdb_score":6.5},
    {"title":"Horimiya: The Missing Pieces","year":2023,"director":"Masashi Ishihama","categories":["romance_drama","comedy_satirical"],"mal_score":7.5,"imdb_score":7.0},
    {"title":"Tokyo Ghoul: Jack","year":2015,"director":"Shuhei Morita","categories":["action_epic","horror_thriller"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"Rurouni Kenshin: The Motion Picture","year":1997,"director":"Kazuhiro Furuhashi","categories":["action_epic","historical"],"mal_score":7.2,"imdb_score":6.8},
    {"title":"Rurouni Kenshin: The Beginning","year":2021,"director":"Keishi Otomo","categories":["action_epic","historical","emotional_slice"],"mal_score":8.2,"imdb_score":7.8},
    {"title":"Vampire Hunter D","year":1985,"director":"Toyoo Ashida","categories":["horror_thriller","fantasy_adventure"],"mal_score":7.2,"imdb_score":6.9},
    {"title":"Wicked City","year":1987,"director":"Yoshiaki Kawajiri","categories":["horror_thriller","action_epic","cyberpunk"],"mal_score":7.0,"imdb_score":6.7},
    {"title":"Demon City Shinjuku","year":1988,"director":"Yoshiaki Kawajiri","categories":["horror_thriller","action_epic","cyberpunk"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"The Five Star Stories","year":1989,"director":"Kazuo Yamazaki","categories":["sci_fi","action_epic","mecha"],"mal_score":6.5,"imdb_score":6.2},
    {"title":"Cyber City Oedo 808","year":1990,"director":"Yoshiaki Kawajiri","categories":["cyberpunk","action_epic","horror_thriller"],"mal_score":7.0,"imdb_score":6.7},
    {"title":"Doomed Megalopolis","year":1991,"director":"Rintaro","categories":["horror_thriller","sci_fi","historical"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"Spirit of Wonder","year":1992,"director":"Takashi Anno","categories":["sci_fi","fantasy_adventure"],"mal_score":6.5,"imdb_score":6.2},
    {"title":"Catnapped!","year":1995,"director":"Takashi Anno","categories":["fantasy_adventure","comedy_satirical"],"mal_score":6.2,"imdb_score":5.9},
    {"title":"Spring and Chaos","year":1996,"director":"Shoji Kawamori","categories":["historical","emotional_slice"],"mal_score":6.5,"imdb_score":6.2},
    {"title":"Princess Arete","year":2001,"director":"Sunao Katabuchi","categories":["fantasy_adventure","emotional_slice"],"mal_score":7.0,"imdb_score":6.7},
    {"title":"The Place Promised in Our Early Days","year":2004,"director":"Makoto Shinkai","categories":["sci_fi","romance_drama","emotional_slice"],"mal_score":7.02,"imdb_score":6.9},
    {"title":"Voices of a Distant Star","year":2002,"director":"Makoto Shinkai","categories":["sci_fi","romance_drama","emotional_slice"],"mal_score":7.18,"imdb_score":7.2},
    {"title":"She and Her Cat","year":1999,"director":"Makoto Shinkai","categories":["emotional_slice","short_film"],"mal_score":7.15,"imdb_score":7.0},
    {"title":"Ninja Scroll","year":1993,"director":"Yoshiaki Kawajiri","categories":["action_epic","historical","horror_thriller"],"mal_score":7.5,"imdb_score":7.4},
    {"title":"Vampire Hunter D: Bloodlust","year":2000,"director":"Yoshiaki Kawajiri","categories":["horror_thriller","action_epic","fantasy_adventure"],"mal_score":7.6,"imdb_score":7.4},
    {"title":"Highlander: The Search for Vengeance","year":2007,"director":"Yoshiaki Kawajiri","categories":["action_epic","fantasy_adventure"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"Afro Samurai: Resurrection","year":2009,"director":"Fuminori Kizaki","categories":["action_epic","historical"],"mal_score":6.5,"imdb_score":6.2},
    {"title":"The Tibetan Dog","year":2011,"director":"Masayuki Kojima","categories":["emotional_slice","fantasy_adventure"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"The Life of Budori Gusuko","year":2012,"director":"Gisaburo Sugii","categories":["fantasy_adventure","emotional_slice"],"mal_score":6.5,"imdb_score":6.2},
    {"title":"Patema Inverted","year":2013,"director":"Yasuhiro Yoshiura","categories":["sci_fi","fantasy_adventure","romance_drama"],"mal_score":7.5,"imdb_score":7.1},
    {"title":"Time of Eve: The Movie","year":2010,"director":"Yasuhiro Yoshiura","categories":["sci_fi","philosophical_surreal","emotional_slice"],"mal_score":7.5,"imdb_score":7.1},
    {"title":"Harmony","year":2015,"director":"Michael Arias","categories":["sci_fi","philosophical_surreal"],"mal_score":7.2,"imdb_score":6.8},
    {"title":"Genocidal Organ","year":2017,"director":"Shukou Murase","categories":["sci_fi","philosophical_surreal","action_epic"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"Napping Princess","year":2017,"director":"Kenji Kamiyama","categories":["sci_fi","fantasy_adventure"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"Lu Over the Wall","year":2017,"director":"Masaaki Yuasa","categories":["fantasy_adventure","emotional_slice"],"mal_score":7.1,"imdb_score":6.8},
    {"title":"The Night Is Short, Walk on Girl","year":2017,"director":"Masaaki Yuasa","categories":["comedy_satirical","romance_drama","philosophical_surreal"],"mal_score":8.05,"imdb_score":7.6},
    {"title":"Ride Your Wave","year":2019,"director":"Masaaki Yuasa","categories":["romance_drama","emotional_slice","fantasy_adventure"],"mal_score":7.45,"imdb_score":7.0},
    {"title":"Inu-Oh","year":2021,"director":"Masaaki Yuasa","categories":["music_art","historical","philosophical_surreal"],"mal_score":7.6,"imdb_score":7.2},
    {"title":"Penguin Highway","year":2018,"director":"Hiroyasu Ishida","categories":["sci_fi","fantasy_adventure","emotional_slice"],"mal_score":7.2,"imdb_score":6.9},
    {"title":"Josee, the Tiger and the Fish","year":2020,"director":"Kotaro Tamura","categories":["romance_drama","emotional_slice"],"mal_score":7.5,"imdb_score":7.1},
    {"title":"Fortune Favors Lady Nikuko","year":2021,"director":"Ayumu Watanabe","categories":["emotional_slice","comedy_satirical"],"mal_score":6.8,"imdb_score":6.5},
    {"title":"The House of the Lost on the Cape","year":2021,"director":"Shinichiro Watanabe","categories":["fantasy_adventure","emotional_slice"],"mal_score":6.5,"imdb_score":6.2},
    {"title":"Totto-chan: The Little Girl at the Window","year":2023,"director":"Shinnosuke Yakuwa","categories":["emotional_slice","historical"],"mal_score":7.2,"imdb_score":6.8},
    {"title":"The Imaginary","year":2023,"director":"Yoshiyuki Momose","categories":["fantasy_adventure","emotional_slice"],"mal_score":7.5,"imdb_score":7.1},
    {"title":"Look Back","year":2024,"director":"Kiyotaka Oshiyama","categories":["emotional_slice","short_film"],"mal_score":8.5,"imdb_score":8.0},
    {"title":"Mononoke the Movie: Phantom in the Rain","year":2024,"director":"Kenji Nakamura","categories":["horror_thriller","philosophical_surreal","historical"],"mal_score":7.8,"imdb_score":7.5},
    {"title":"The Colors Within","year":2024,"director":"Naoko Yamada","categories":["emotional_slice","music_art"],"mal_score":7.7,"imdb_score":7.3},
    {"title":"Sailor Moon Cosmos Part 1","year":2024,"director":"Kazuko Tadano","categories":["fantasy_adventure","romance_drama"],"mal_score":7.5,"imdb_score":7.0},
    {"title":"Sailor Moon Cosmos Part 2","year":2024,"director":"Kazuko Tadano","categories":["fantasy_adventure","romance_drama"],"mal_score":7.5,"imdb_score":7.0},
    {"title":"Chainsaw Man: Reze Arc","year":2025,"director":"Tatsuya Yoshihara","categories":["action_epic","horror_thriller"],"mal_score":9.13,"imdb_score":8.5},
    {"title":"Madoka Magica: The Movie – Walpurgisnacht: Rising","year":2025,"director":"Akiyuki Shinbo","categories":["philosophical_surreal","fantasy_adventure","action_epic"],"mal_score":8.5,"imdb_score":8.0},
]

# === FONKSİYONLAR ===
def is_watched(t):
    t2 = t.lower().strip()
    return t2 in WATCHED or any(t2 in w or w in t2 for w in WATCHED)

def taste_score(cats):
    if not cats: return 5.0
    return round(sum(TASTE_W.get(c,5) for c in cats)/len(cats), 1)

def owl_score(mal, imdb, cats):
    base = (mal*0.6 + imdb*0.4) if imdb > 0 else mal
    return min(round(base + taste_score(cats)*0.1, 1), 10.0)

def get_source(t):
    k = {"akira":"Manga","ghost in the shell":"Manga","perfect blue":"Novel","spirited away":"Original","princess mononoke":"Original","my neighbor totoro":"Original","howl's moving castle":"Novel","castle in the sky":"Original","kiki's delivery service":"Novel","nausicaa of the valley of the wind":"Manga","grave of the fireflies":"Novel","only yesterday":"Manga","paprika":"Novel","millennium actress":"Original","tokyo godfathers":"Original","a silent voice":"Manga","wolf children":"Original","the girl who leapt through time":"Novel","summer wars":"Original","belle":"Original","redline":"Original","promare":"Original","mind game":"Manga","tekkonkinkreet":"Manga","in this corner of the world":"Manga","maquia: when the promised flower blooms":"Original","jujutsu kaisen 0":"Manga","the first slam dunk":"Manga","sword of the stranger":"Original","violet evergarden":"Light Novel","liz and the blue bird":"Light Novel","kizumonogatari":"Light Novel","madoka magica: rebellion":"Original","ride your wave":"Original","the night is short, walk on girl":"Novel","inu-oh":"Novel","children of the sea":"Manga","fate/stay night: heaven's feel":"Visual Novel","one piece: stampede":"Manga","one piece film: red":"Manga","spy x family code: white":"Manga","chainsaw man: reze arc":"Manga","the boy and the heron":"Novel","mononoke the movie":"TV Series","sailor moon cosmos":"Manga","sailor moon eternal":"Manga","digimon adventure: last evolution kizuna":"Original","my hero academia: two heroes":"Manga","my hero academia: heroes rising":"Manga","my hero academia: world heroes mission":"Manga","detective conan: the fist of blue sapphire":"Manga","detective conan: zero the enforcer":"Manga","lupin iii: the first":"Manga","arrietty":"Novel","when marnie was there":"Novel","mary and the witch's flower":"Novel","tales from earthsea":"Novel","from up on poppy hill":"Manga","the colors within":"Original","tamako love story":"Original","k-on! the movie":"Manga","patlabor: the movie":"Original","patlabor 2: the movie":"Original","jin-roh: the wolf brigade":"Original","blood: the last vampire":"Original","ninja scroll":"Original","vampire hunter d: bloodlust":"Novel","x/1999":"Manga","cardcaptor sakura: the movie":"Manga","escaflowne: the movie":"TV Series","berserk: golden age arc":"Manga","mobile suit gundam: char's counterattack":"TV Series","mobile suit gundam: hathaway":"Novel","rurouni kenshin: trust & betrayal":"Manga","gurren lagann: childhood's end":"TV Series","royal space force: the wings of honneamise":"Original","angel's egg":"Original","urusei yatsura 2: beautiful dreamer":"Manga","the sky crawlers":"Novel","avalon":"Original","steamboy":"Original","roujin z":"Original","memories":"Manga","metropolis":"Manga","gunbuster":"Original","diebuster":"Original","knights of sidonia":"Manga","blame!":"Manga","modest heroes":"Original","tomorrow's joe":"Manga","sword art online: ordinal scale":"Light Novel","sword art online: progressive - aria of a starless night":"Light Novel","garden of sinners: overlooking view":"Novel","garden of sinners: remaining sense of pain":"Novel","garden of sinners: the hollow shrine":"Novel","garden of sinners: paradox spiral":"Novel","shin godzilla":"Original","shin ultaman":"Original","shin kamen rider":"Original","attack on titan: chronicle":"Manga","ranking of kings: the treasure chest of courage":"Manga","zombie land saga: revenge":"Original","colorful":"Novel","summer days with coo":"Original","miss hokusai":"Manga","anthem of the heart":"Original","her blue sky":"Original","free! take your marks":"TV Series","little witch academia":"Original","kill la kill: if":"TV Series","cowboy bebop: the movie":"TV Series","fullmetal alchemist: the sacred star of milos":"Manga","psycho-pass: the movie":"TV Series","009 re:cyborg":"Manga","kabaneri of the iron fortress: the battle of unato":"TV Series","saga of tanya the evil: the movie":"Light Novel","attack on titan: the roar of awakening":"Manga","clannad: the movie":"Visual Novel","the disappearance of haruhi suzumiya":"Light Novel","sound! euphonium: the movie":"Light Novel","your name":"Original","weathering with you":"Original","suzume":"Original","5 centimeters per second":"Original","the garden of words":"Original","children who chase lost voices":"Original","the place promised in our early days":"Original","voices of a distant star":"Original","she and her cat":"Original","the tatami galaxy":"Novel","the end of evangelion":"TV Series","evangelion: 1.0 you are (not) alone":"TV Series","evangelion: 2.0 you can (not) advance":"TV Series","evangelion: 3.0 you can (not) redo":"TV Series","evangelion: 3.0+1.0 thrice upon a time":"TV Series"}
    for key, src in k.items():
        if key in t.lower(): return src
    return "Manga/Light Novel/Original"

def has_wn(t):
    wns = ["mushoku tensei","re:zero","overlord","that time i got reincarnated as a slime","the rising of the shield hero","no game no life","sword art online","log horizon","konosuba","grimgar","ascendance of a bookworm","solo leveling","omniscient reader","second life ranker","tomb raider king","the beginning after the end","lord of the mysteries","shadow slave","eleceed","nano machine","return of the disaster-class hero","sss-class suicide hunter","the greatest estate developer","doctor's rebirth","heavenly demon cultivation simulation","regression instinct","infinite mage","the s-classes that i raised","the novels extra","trash of the count's family","the world after the fall","kill the hero"]
    return any(w in t.lower() for w in wns)

def why_selected(cats, year):
    r = []
    m = {"philosophical_surreal":"Felsefi derinlik ve surreal anlatim (Lain tarzi)","psychological":"Psikolojik gerilim ve zihin oyunlari","cyberpunk":"Cyberpunk estetigi ve teknoloji felsefesi","action_epic":"Epik aksiyon ve muthis sahneler","emotional_slice":"Duygusal derinlik ve insani hikaye","fantasy_adventure":"Yaratici fantastik dunya","comedy_satirical":"Zekice komedi ve satirik anlatim","sci_fi":"Bilim kurgu vizyonu","mystery":"Gizem ve gerilim kurgusu","music_art":"Muzik/sanat temali yaratici konsept","historical":"Tarihi derinlik ve otantik atmosfer","horror_thriller":"Karanlik atmosfer ve gerilim","sports":"Spor temali motivasyon ve heyecan","mecha":"Mekka tasarimi ve aksiyon","short_film":"Kisa ve etkili anlatim"}
    for c in cats:
        if c in m: r.append(m[c])
    if year >= 2020: r.append("Yeni cikan, guncel animasyon teknolojisi")
    elif year < 1990: r.append("Klasik, tarihi oneme sahip eser")
    return "; ".join(r[:3]) if r else "Genel kalite ve izleyici begeni orani"

def critic_review(mal):
    if mal >= 8.5: return "Basyapit kabul edilir. Animasyon, kurgu ve karakter derinligi mukemmel."
    elif mal >= 8.0: return "Cok yuksek kaliteli. Hem gorsel hem anlatimsal acidan ust duzey."
    elif mal >= 7.5: return "Yuksek kalite. Turunun en iyi orneklerinden."
    elif mal >= 7.0: return "Iyi yapim. Zevk profiline uygun, keyifli izleme."
    elif mal >= 6.5: return "Ortalamanin uzerinde. Bazi guclu yonleri var."
    else: return "Degerlendirme karmasik. Belirli bir izleyici kitlesine hitap edebilir."

def anim_q(year):
    if year >= 2020: return "Cok Yuksek (Modern dijital)"
    elif year >= 2010: return "Yuksek (Dijital)"
    elif year >= 2000: return "Iyi (Gecis donemi)"
    elif year >= 1990: return "Iyi (Geleneksel)"
    else: return "Tarihi deger (Erken donem)"

def pop(mal):
    if mal >= 8.5: return "Cok Populer (Top 100)"
    elif mal >= 8.0: return "Populer (Top 500)"
    elif mal >= 7.5: return "Iyi Bilinen (Top 1000)"
    elif mal >= 7.0: return "Nispeten Bilinen (Top 5000)"
    else: return "Az Bilinen (Gizemli Mucevher)"

def taste_idx(cats):
    if "philosophical_surreal" in cats or "psychological" in cats: return "Lain, Perfect Blue, Evangelion severler icin"
    elif "action_epic" in cats: return "Dragon Ball, Demon Slayer, Solo Leveling severler icin"
    elif "emotional_slice" in cats: return "Mushishi, Dororo, Violet Evergarden severler icin"
    elif "comedy_satirical" in cats: return "Gintama, Konosuba severler icin"
    elif "cyberpunk" in cats or "sci_fi" in cats: return "Akira, Ghost in the Shell severler icin"
    elif "fantasy_adventure" in cats: return "Studio Ghibli, Dororo severler icin"
    else: return "Genel anime severler icin"

def char_depth(cats):
    if "psychological" in cats or "philosophical_surreal" in cats: return "Cok Derin (Psikolojik profil, ic catisma)"
    elif "emotional_slice" in cats: return "Derin (Duygusal gelisim, iliskiler)"
    elif "action_epic" in cats: return "Iyi (Guc gelisim, motivasyon)"
    elif "comedy_satirical" in cats: return "Iyi (Karakter tabanli mizah)"
    else: return "Orta (Tur geregi yeterli)"

def story_q(cats):
    if "philosophical_surreal" in cats: return "Cok Yuksek (Katmanli anlatim, sembolizm)"
    elif "psychological" in cats: return "Yuksek (Surukleyici, sürprizler)"
    elif "mystery" in cats: return "Yuksek (Gizem, ipuclari, cozum)"
    elif "action_epic" in cats: return "Iyi (Tempo, gerilim, doruk noktasi)"
    elif "emotional_slice" in cats: return "Yuksek (Doyurucu, dokunakli)"
    else: return "Iyi (Tur standartlarini karsiliyor)"

# === ANA İŞLEM ===
print("="*60)
print("OWL - KAPSAMLI ANIME FILM ANALIZ SISTEMI v1.0")
print("="*60)

# Duplicate temizleme
seen = set()
unique = []
for f in FILMS:
    key = f"{f.get('title', f.get('t', '')).lower()}_{f.get('year', f.get('y', 2000))}"
    if key not in seen:
        seen.add(key)
        unique.append(f)

# İzlenenleri çıkar
filtered = [f for f in unique if not is_watched(f.get("title", f.get("t", "")))]
print(f"Toplam film: {len(unique)}")
print(f"Izlenen cikarildi: {len(unique)-len(filtered)}")
print(f"Kalani: {len(filtered)}")

# Analiz üret
analyzed = []
for f in filtered:
    mal = f.get("mal_score", f.get("mal", 7.0))
    imdb = f.get("imdb_score", f.get("imdb", 0))
    cats = f.get("categories", f.get("cat", []))
    year = f.get("year", f.get("y", 2000))
    title = f.get("t", f.get("title", ""))
    
    analyzed.append({
        "title": title,
        "year": year,
        "director": f.get("director", f.get("d", "")),
        "categories": cats,
        "category_names": [CATS.get(c,c) for c in cats],
        "mal_score": mal,
        "imdb_score": imdb,
        "owl_score": owl_score(mal, imdb, cats),
        "taste_score": taste_score(cats),
        "source_material": get_source(title),
        "has_web_novel": has_wn(title),
        "why_selected": why_selected(cats, year),
        "critic_review": critic_review(mal),
        "animation_quality": anim_q(year),
        "popularity": pop(mal),
        "taste_index": taste_idx(cats),
        "character_depth": char_depth(cats),
        "story_quality": story_q(cats),
    })

analyzed.sort(key=lambda x: x["owl_score"], reverse=True)
print(f"Analiz tamamlandi: {len(analyzed)} film")

# === TXT RAPORLARI ===
print("\nTXT raporlari olusturuluyor...")

# 1. Ana liste
with open(f"{BASE}/output/txt/01_ana_liste_owl.txt","w",encoding="utf-8") as f:
    f.write("="*80+"\nOWL - KAPSAMLI ANIME FILM LISTESI (OWL Puana Gore)\n")
    f.write(f"Olusturulma: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Toplam: {len(analyzed)}\n"+"="*80+"\n\n")
    for i,film in enumerate(analyzed,1):
        f.write(f"#{i:04d} | OWL:{film['owl_score']:.1f} | MAL:{film['mal_score']:.1f}\n")
        f.write(f"Film: {film['title']} ({film['year']})\n")
        f.write(f"Yonetmen: {film['director']}\n")
        f.write(f"Tur: {', '.join(film['category_names'])}\n")
        f.write(f"Kaynak: {film['source_material']} | WN: {'Evet' if film['has_web_novel'] else 'Hayir'}\n")
        f.write(f"Populerlik: {film['popularity']}\n")
        f.write(f"Neden: {film['why_selected']}\n")
        f.write(f"Kritik: {film['critic_review']}\n")
        f.write(f"Animasyon: {film['animation_quality']}\n")
        f.write(f"Karakter: {film['character_depth']} | Kurgu: {film['story_quality']}\n")
        f.write(f"Benzer Zevk: {film['taste_index']}\n")
        f.write("-"*80+"\n\n")
print("  01_ana_liste_owl.txt")

# 2. Kategori bazlı
for ck, cn in CATS.items():
    cf = sorted([f for f in analyzed if ck in f["categories"]], key=lambda x: x["owl_score"], reverse=True)
    if cf:
        with open(f"{BASE}/output/txt/02_kategori_{ck}.txt","w",encoding="utf-8") as f:
            f.write(f"KATEGORI: {cn} ({len(cf)} film)\n"+"="*80+"\n\n")
            for i,film in enumerate(cf,1):
                f.write(f"#{i:03d} | OWL:{film['owl_score']:.1f} | {film['title']} ({film['year']})\n")
                f.write(f"  Yonetmen: {film['director']} | Kaynak: {film['source_material']}\n")
                f.write(f"  Neden: {film['why_selected']}\n")
                f.write(f"  Kritik: {film['critic_review']}\n"+"-"*60+"\n")
print("  02_kategori_*.txt")

# 3. Yıl bazlı
for year in sorted(set(f["year"] for f in analyzed)):
    yf = sorted([f for f in analyzed if f["year"]==year], key=lambda x: x["owl_score"], reverse=True)
    if yf:
        with open(f"{BASE}/output/txt/03_yil_{year}.txt","w",encoding="utf-8") as f:
            f.write(f"{year} YILI ANIME FILMLERI ({len(yf)} film)\n"+"="*80+"\n\n")
            for film in yf:
                f.write(f"OWL:{film['owl_score']:.1f} | {film['title']}\n")
                f.write(f"  Yonetmen: {film['director']} | Tur: {', '.join(film['category_names'])}\n")
                f.write(f"  Neden: {film['why_selected']}\n\n")
print("  03_yil_*.txt")

# 4. Web Novel
wn = sorted([f for f in analyzed if f["has_web_novel"]], key=lambda x: x["owl_score"], reverse=True)
with open(f"{BASE}/output/txt/04_web_novel.txt","w",encoding="utf-8") as f:
    f.write(f"WEB NOVEL KAYNAKLI FILMLER ({len(wn)} film)\n"+"="*80+"\n\n")
    for film in wn:
        f.write(f"OWL:{film['owl_score']:.1f} | {film['title']} ({film['year']})\n")
        f.write(f"  Kaynak: {film['source_material']}\n")
        f.write(f"  Neden: {film['why_selected']}\n\n")
print("  04_web_novel.txt")

# 5. Kaynak malzeme
srcs = {}
for f in analyzed:
    s = f["source_material"]
    srcs.setdefault(s, []).append(f)
with open(f"{BASE}/output/txt/05_kaynak.txt","w",encoding="utf-8") as f:
    f.write("KAYNAK MALZEME BAZLI\n"+"="*80+"\n\n")
    for s in sorted(srcs.keys()):
        films = sorted(srcs[s], key=lambda x: x["owl_score"], reverse=True)
        f.write(f"\n--- {s} ({len(films)} film) ---\n")
        for film in films[:20]:
            f.write(f"  OWL:{film['owl_score']:.1f} | {film['title']} ({film['year']})\n")
print("  05_kaynak.txt")

# 6. İstatistik
with open(f"{BASE}/output/stats/istatistik.txt","w",encoding="utf-8") as f:
    f.write("OWL - ISTATISTIKLER\n"+"="*80+"\n\n")
    f.write(f"TOPLAM FILM: {len(analyzed)}\n\n")
    f.write("--- TUR DAGILIMI ---\n")
    for ck, cn in CATS.items():
        c = len([f for f in analyzed if ck in f["categories"]])
        if c: f.write(f"  {cn}: {c} ({c/len(analyzed)*100:.1f}%)\n")
    f.write("\n--- YIL DAGILIMI ---\n")
    dc = {}
    for film in analyzed:
        d = (film["year"]//10)*10
        dc[d] = dc.get(d,0)+1
    for d in sorted(dc): f.write(f"  {d}ler: {dc[d]}\n")
    f.write("\n--- PUAN DAGILIMI ---\n")
    for lo,hi in [(9,10),(8.5,9),(8,8.5),(7.5,8),(7,7.5),(0,7)]:
        c = len([f for f in analyzed if lo<=f["owl_score"]<hi])
        if c: f.write(f"  {lo:.1f}-{hi:.1f}: {c}\n")
    f.write(f"\n--- WEB NOVEL: {len(wn)} film ---\n")
    f.write("\n--- EN IYI 20 ---\n")
    for i,film in enumerate(analyzed[:20],1):
        f.write(f"  {i:2d}. {film['title']} ({film['year']}) OWL:{film['owl_score']:.1f}\n")
print("  istatistik.txt")

# 7. Özet
with open(f"{BASE}/output/OZET_RAPOR.txt","w",encoding="utf-8") as f:
    f.write("="*80+"\nOWL - KAPSAMLI ANIME FILM ANALIZI - OZET RAPOR\n")
    f.write(f"Olusturulma: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"+"="*80+"\n\n")
    f.write(f"Toplam analiz: {len(analyzed)} film\n")
    f.write(f"Web Novel kaynakli: {len(wn)}\n")
    f.write(f"Yil araligi: {min(f['year'] for f in analyzed)}-{max(f['year'] for f in analyzed)}\n\n")
    f.write("ONERILER:\n")
    f.write("1. Felsefi/Surreal kategorisindeki yuksek puanli filmlerle baslayin\n")
    f.write("2. Web Novel kaynakli filmleri okuyarak derinlesin\n")
    f.write("3. Yonetmen kariyerlerini takip edin\n")
    f.write("4. Kategori cesitliligini koruyun\n\n")
    f.write("DOSYALAR:\n")
    f.write("- 01_ana_liste_owl.txt: Tum filmler OWL puanina gore\n")
    f.write("- 02_kategori_*.txt: Kategori bazli listeler\n")
    f.write("- 03_yil_*.txt: Yil bazli listeler\n")
    f.write("- 04_web_novel.txt: Web Novel kaynakli filmler\n")
    f.write("- 05_kaynak.txt: Kaynak malzeme bazli\n")
    f.write("- istatistik.txt: Detayli istatistikler\n")
print("  OZET_RAPOR.txt")

# JSON kaydet
with open(f"{BASE}/data/analyzed_films.json","w",encoding="utf-8") as f:
    json.dump(analyzed, f, ensure_ascii=False, indent=2)

print(f"\nJSON: {BASE}/data/analyzed_films.json")
txt_count = len([f for f in os.listdir(f"{BASE}/output/txt") if f.endswith(".txt")])
print(f"Toplam {txt_count} TXT dosyasi")
print(f"Toplam {len(analyzed)} film analiz edildi")
print("\n=== ISLEM TAMAMLANDI ===")
