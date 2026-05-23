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
    {"t":"The Little Prince and the Eight-Headed Dragon","y":1963,"d":"Yugo Serikawa","cat":["fantasy_adventure"],"mal":6.5,"imdb":6.2},
    {"t":"Hols: Prince of the Sun","y":1968,"d":"Isao Takahata","cat":["fantasy_adventure","action_epic"],"mal":7.5,"imdb":7.2},
    {"t":"The Wonderful World of Puss 'n Boots","y":1969,"d":"Kimio Yabuki","cat":["fantasy_adventure","comedy_satirical"],"mal":6.8,"imdb":6.5},
    {"t":"Cleopatra","y":1970,"d":"Eiichi Yamamoto","cat":["historical","fantasy_adventure"],"mal":6.2,"imdb":5.9},
    {"t":"Belladonna of Sadness","y":1973,"d":"Eiichi Yamamoto","cat":["philosophical_surreal","historical","horror_thriller"],"mal":7.5,"imdb":7.3},
    {"t":"Space Battleship Yamato","y":1977,"d":"Toshio Masuda","cat":["sci_fi","action_epic"],"mal":7.5,"imdb":7.2},
    {"t":"Lupin III: The Castle of Cagliostro","y":1979,"d":"Hayao Miyazaki","cat":["action_epic","fantasy_adventure"],"mal":7.8,"imdb":7.6},
    {"t":"Galaxy Express 999","y":1979,"d":"Rintaro","cat":["sci_fi","fantasy_adventure"],"mal":7.5,"imdb":7.2},
    {"t":"Adieu Galaxy Express 999","y":1981,"d":"Rintaro","cat":["sci_fi","emotional_slice"],"mal":7.2,"imdb":6.9},
    {"t":"Arcadia of My Youth","y":1982,"d":"Tomoharu Katsumata","cat":["sci_fi","action_epic"],"mal":7.3,"imdb":7.0},

    # --- 1980-1990 ---
    {"t":"Phoenix 2772","y":1980,"d":"Sugii Gisaburo","cat":["sci_fi","romance_drama"],"mal":6.8,"imdb":6.5},
    {"t":"Doraemon: Nobita's Little Star Wars","y":1985,"d":"Tsutomu Shibayama","cat":["sci_fi","comedy_satirical"],"mal":6.8,"imdb":6.5},
    {"t":"Nausicaa of the Valley of the Wind","y":1984,"d":"Hayao Miyazaki","cat":["fantasy_adventure","sci_fi","emotional_slice"],"mal":8.33,"imdb":8.0},
    {"t":"Castle in the Sky","y":1986,"d":"Hayao Miyazaki","cat":["fantasy_adventure","action_epic"],"mal":8.18,"imdb":8.0},
    {"t":"My Neighbor Totoro","y":1988,"d":"Hayao Miyazaki","cat":["emotional_slice","fantasy_adventure"],"mal":8.25,"imdb":8.1},
    {"t":"Kikis Delivery Service","y":1989,"d":"Hayao Miyazaki","cat":["fantasy_adventure","emotional_slice"],"mal":8.18,"imdb":7.8},
    {"t":"Grave of the Fireflies","y":1988,"d":"Isao Takahata","cat":["emotional_slice","historical"],"mal":8.5,"imdb":8.5},
    {"t":"Akira","y":1988,"d":"Katsuhiro Otomo","cat":["cyberpunk","sci_fi","action_epic","philosophical_surreal"],"mal":8.15,"imdb":8.0},
    {"t":"Urusei Yatsura 2: Beautiful Dreamer","y":1984,"d":"Mamoru Oshii","cat":["philosophical_surreal","comedy_satirical"],"mal":7.55,"imdb":7.4},
    {"t":"Angel's Egg","y":1985,"d":"Mamoru Oshii","cat":["philosophical_surreal","emotional_slice"],"mal":7.45,"imdb":7.3},
    {"t":"Patlabor: The Movie","y":1989,"d":"Mamoru Oshii","cat":["mecha","sci_fi","action_epic"],"mal":7.58,"imdb":7.1},
    {"t":"Mobile Suit Gundam: Char's Counterattack","y":1988,"d":"Yoshiyuki Tomino","cat":["mecha","sci_fi","action_epic"],"mal":7.8,"imdb":7.5},
    {"t":"Vampire Hunter D","y":1985,"d":"Toyoo Ashida","cat":["horror_thriller","fantasy_adventure"],"mal":7.2,"imdb":6.9},
    {"t":"Wicked City","y":1987,"d":"Yoshiaki Kawajiri","cat":["horror_thriller","action_epic","cyberpunk"],"mal":7.0,"imdb":6.7},
    {"t":"Demon City Shinjuku","y":1988,"d":"Yoshiaki Kawajiri","cat":["horror_thriller","action_epic","cyberpunk"],"mal":6.8,"imdb":6.5},
    {"t":"The Five Star Stories","y":1989,"d":"Kazuo Yamazaki","cat":["sci_fi","action_epic","mecha"],"mal":6.5,"imdb":6.2},
    {"t":"Tailender","y":1988,"d":"Tetsuro Imazawa","cat":["sci_fi","action_epic"],"mal":5.8,"imdb":5.5},

    # --- 1990-2000 ---
    {"t":"Only Yesterday","y":1991,"d":"Isao Takahata","cat":["emotional_slice","romance_drama"],"mal":7.94,"imdb":7.6},
    {"t":"Pom Poko","y":1994,"d":"Isao Takahata","cat":["fantasy_adventure","comedy_satirical"],"mal":7.1,"imdb":7.3},
    {"t":"Whisper of the Heart","y":1995,"d":"Yoshifumi Kondo","cat":["romance_drama","emotional_slice"],"mal":8.22,"imdb":7.8},
    {"t":"The Cat Returns","y":2002,"d":"Hiroyuki Morita","cat":["fantasy_adventure","comedy_satirical"],"mal":7.53,"imdb":7.2},
    {"t":"Princess Mononoke","y":1997,"d":"Hayao Miyazaki","cat":["fantasy_adventure","action_epic","historical"],"mal":8.66,"imdb":8.3},
    {"t":"Ocean Waves","y":1993,"d":"Tomomi Mochizuki","cat":["romance_drama","emotional_slice"],"mal":6.89,"imdb":6.8},
    {"t":"My Neighbors the Yamadas","y":1999,"d":"Isao Takahata","cat":["comedy_satirical","emotional_slice"],"mal":7.33,"imdb":7.1},
    {"t":"Perfect Blue","y":1997,"d":"Satoshi Kon","cat":["psychological","horror_thriller","philosophical_surreal"],"mal":8.54,"imdb":8.0},
    {"t":"Ghost in the Shell","y":1995,"d":"Mamoru Oshii","cat":["cyberpunk","sci_fi","philosophical_surreal","action_epic"],"mal":8.27,"imdb":7.9},
    {"t":"Ghost in the Shell 2: Innocence","y":2004,"d":"Mamoru Oshii","cat":["cyberpunk","philosophical_surreal","sci_fi"],"mal":7.63,"imdb":7.4},
    {"t":"Patlabor 2: The Movie","y":1993,"d":"Mamoru Oshii","cat":["mecha","sci_fi","philosophical_surreal"],"mal":7.72,"imdb":7.3},
    {"t":"Jin-Roh: The Wolf Brigade","y":1999,"d":"Hiroyuki Okiura","cat":["action_epic","philosophical_surreal","historical"],"mal":7.6,"imdb":7.3},
    {"t":"Ninja Scroll","y":1993,"d":"Yoshiaki Kawajiri","cat":["action_epic","historical","horror_thriller"],"mal":7.5,"imdb":7.4},
    {"t":"Vampire Hunter D: Bloodlust","y":2000,"d":"Yoshiaki Kawajiri","cat":["horror_thriller","action_epic","fantasy_adventure"],"mal":7.6,"imdb":7.4},
    {"t":"Cardcaptor Sakura: The Movie","y":1999,"d":"Morio Asaka","cat":["fantasy_adventure","romance_drama"],"mal":7.8,"imdb":7.4},
    {"t":"Cardcaptor Sakura Movie 2: The Sealed Card","y":2000,"d":"Morio Asaka","cat":["fantasy_adventure","romance_drama"],"mal":8.0,"imdb":7.6},
    {"t":"Revolutionary Girl Utena: Adolescence of Utena","y":1999,"d":"Kunihiko Ikuhara","cat":["philosophical_surreal","psychological","romance_drama"],"mal":7.8,"imdb":7.4},
    {"t":"Love Hina Again","y":2002,"d":"Yoshiaki Iwasaki","cat":["comedy_satirical","romance_drama"],"mal":6.8,"imdb":6.5},
    {"t":"Rurouni Kenshin: Trust and Betrayal","y":1999,"d":"Kazuhiro Furuhashi","cat":["action_epic","historical","emotional_slice"],"mal":8.7,"imdb":8.3},
    {"t":"The Vision of Escaflowne","y":2000,"d":"Kazuki Akane","cat":["fantasy_adventure","mecha","romance_drama"],"mal":7.3,"imdb":7.0},
    {"t":"Record of Lodoss War: Chronicles of the Heroic Knight","y":1998,"d":"Kunihiko Yuyama","cat":["fantasy_adventure","action_epic"],"mal":7.0,"imdb":6.7},
    {"t":"Legend of the Galactic Heroes: My Conquest is the Sea of Stars","y":1988,"d":"Noboru Ishiguro","cat":["sci_fi","historical","action_epic"],"mal":7.2,"imdb":6.9},
    {"t":"Spriggan","y":1998,"d":"Masahiko Murata","cat":["action_epic","sci_fi"],"mal":6.8,"imdb":6.5},
    {"t":"X/1999","y":1996,"d":"Rintaro","cat":["action_epic","fantasy_adventure","horror_thriller"],"mal":7.2,"imdb":6.8},
    {"t":"Blood: The Last Vampire","y":2000,"d":"Hiroyuki Kitakubo","cat":["horror_thriller","action_epic"],"mal":6.8,"imdb":6.5},
    {"t":"The Laws of the Sun","y":2000,"d":"Takaaki Ishiyama","cat":["sci_fi","fantasy_adventure"],"mal":5.5,"imdb":5.2},

    # --- 2000-2010 ---
    {"t":"Millennium Actress","y":2001,"d":"Satoshi Kon","cat":["philosophical_surreal","emotional_slice","romance_drama"],"mal":8.17,"imdb":7.8},
    {"t":"Tokyo Godfathers","y":2003,"d":"Satoshi Kon","cat":["comedy_satirical","emotional_slice"],"mal":8.1,"imdb":7.8},
    {"t":"Paprika","y":2006,"d":"Satoshi Kon","cat":["philosophical_surreal","sci_fi","psychological"],"mal":8.04,"imdb":7.7},
    {"t":"Spirited Away","y":2001,"d":"Hayao Miyazaki","cat":["fantasy_adventure","emotional_slice"],"mal":8.77,"imdb":8.6},
    {"t":"Howls Moving Castle","y":2004,"d":"Hayao Miyazaki","cat":["fantasy_adventure","romance_drama"],"mal":8.58,"imdb":8.2},
    {"t":"Tales from Earthsea","y":2006,"d":"Goro Miyazaki","cat":["fantasy_adventure"],"mal":6.53,"imdb":6.4},
    {"t":"Ponyo","y":2008,"d":"Hayao Miyazaki","cat":["fantasy_adventure","emotional_slice"],"mal":7.89,"imdb":7.6},
    {"t":"The Place Promised in Our Early Days","y":2004,"d":"Makoto Shinkai","cat":["sci_fi","romance_drama","emotional_slice"],"mal":7.02,"imdb":6.9},
    {"t":"5 Centimeters Per Second","y":2007,"d":"Makoto Shinkai","cat":["romance_drama","emotional_slice"],"mal":7.56,"imdb":7.5},
    {"t":"Voices of a Distant Star","y":2002,"d":"Makoto Shinkai","cat":["sci_fi","romance_drama","emotional_slice"],"mal":7.18,"imdb":7.2},
    {"t":"The Girl Who Leapt Through Time","y":2006,"d":"Mamoru Hosoda","cat":["sci_fi","romance_drama","emotional_slice"],"mal":8.1,"imdb":7.7},
    {"t":"Summer Wars","y":2009,"d":"Mamoru Hosoda","cat":["sci_fi","comedy_satirical","emotional_slice"],"mal":7.9,"imdb":7.5},
    {"t":"Tekkonkinkreet","y":2006,"d":"Michael Arias","cat":["action_epic","philosophical_surreal","emotional_slice"],"mal":7.8,"imdb":7.4},
    {"t":"Mind Game","y":2004,"d":"Masaaki Yuasa","cat":["philosophical_surreal","comedy_satirical","psychological"],"mal":7.85,"imdb":7.6},
    {"t":"Redline","y":2009,"d":"Takeshi Koike","cat":["action_epic","sci_fi","comedy_satirical"],"mal":8.2,"imdb":7.7},
    {"t":"Metropolis","y":2001,"d":"Rintaro","cat":["sci_fi","philosophical_surreal"],"mal":7.2,"imdb":7.0},
    {"t":"Steamboy","y":2004,"d":"Katsuhiro Otomo","cat":["sci_fi","action_epic","historical"],"mal":7.02,"imdb":6.8},
    {"t":"Cowboy Bebop: The Movie","y":2001,"d":"Shinichiro Watanabe","cat":["action_epic","sci_fi","cyberpunk"],"mal":8.0,"imdb":7.6},
    {"t":"Fullmetal Alchemist: The Sacred Star of Milos","y":2011,"d":"Kazuya Murata","cat":["action_epic","fantasy_adventure"],"mal":7.5,"imdb":7.1},
    {"t":"Sword of the Stranger","y":2007,"d":"Masahiro Ando","cat":["action_epic","historical"],"mal":8.1,"imdb":7.7},
    {"t":"Colourful","y":2010,"d":"Keiichi Hara","cat":["emotional_slice","philosophical_surreal"],"mal":7.6,"imdb":7.3},
    {"t":"Colorful","y":2010,"d":"Keiichi Hara","cat":["emotional_slice","philosophical_surreal"],"mal":7.6,"imdb":7.3},
    {"t":"Summer Days with Coo","y":2007,"d":"Keiichi Hara","cat":["fantasy_adventure","emotional_slice","comedy_satirical"],"mal":7.4,"imdb":7.1},
    {"t":"The Sky Crawlers","y":2008,"d":"Mamoru Oshii","cat":["sci_fi","philosophical_surreal","action_epic"],"mal":7.15,"imdb":6.8},
    {"t":"Dead Leaves","y":2004,"d":"Hiroyuki Imaishi","cat":["comedy_satirical","sci_fi","action_epic"],"mal":7.1,"imdb":6.8},
    {"t":"Samurai Champloo: The Movie","y":2007,"d":"Shinichiro Watanabe","cat":["action_epic","historical"],"mal":6.8,"imdb":6.5},
    {"t":"Rosario + Vampire CAPU2","y":2008,"d":"Takayuki Inagaki","cat":["comedy_satirical","horror_thriller"],"mal":6.2,"imdb":5.9},

    # --- 2010-2015 ---
    {"t":"Wolf Children","y":2012,"d":"Mamoru Hosoda","cat":["fantasy_adventure","emotional_slice","romance_drama"],"mal":8.55,"imdb":8.2},
    {"title":"From Up on Poppy Hill","y":2011,"d":"Goro Miyazaki","cat":["romance_drama","emotional_slice","historical"],"mal":7.44,"imdb":7.4},
    {"t":"The Wind Rises","y":2013,"d":"Hayao Miyazaki","cat":["historical","romance_drama","emotional_slice"],"mal":7.96,"imdb":7.8},
    {"t":"The Tale of The Princess Kaguya","y":2013,"d":"Isao Takahata","cat":["fantasy_adventure","emotional_slice","historical"],"mal":8.1,"imdb":8.0},
    {"t":"K-On! The Movie","y":2011,"d":"Naoko Yamada","cat":["music_art","comedy_satirical","emotional_slice"],"mal":7.9,"imdb":7.5},
    {"t":"A Silent Voice","y":2016,"d":"Naoko Yamada","cat":["emotional_slice","romance_drama"],"mal":8.9,"imdb":8.2},
    {"t":"The Tatami Galaxy","y":2010,"d":"Masaaki Yuasa","cat":["philosophical_surreal","psychological","comedy_satirical"],"mal":8.45,"imdb":8.1},
    {"t":"Children Who Chase Lost Voices","y":2011,"d":"Makoto Shinkai","cat":["fantasy_adventure","emotional_slice"],"mal":7.33,"imdb":7.1},
    {"t":"The Garden of Words","y":2013,"d":"Makoto Shinkai","cat":["romance_drama","emotional_slice"],"mal":7.48,"imdb":7.4},
    {"t":"Maquia: When the Promised Flower Blooms","y":2018,"d":"Mari Okada","cat":["fantasy_adventure","emotional_slice","romance_drama"],"mal":8.05,"imdb":7.6},
    {"t":"In This Corner of the World","y":2016,"d":"Sunao Katabuchi","cat":["historical","emotional_slice","romance_drama"],"mal":8.15,"imdb":7.8},
    {"t":"Anthem of the Heart","y":2015,"d":"Mari Okada","cat":["emotional_slice","romance_drama","music_art"],"mal":7.8,"imdb":7.4},
    {"t":"Her Blue Sky","y":2019,"d":"Mari Okada","cat":["romance_drama","emotional_slice","fantasy_adventure"],"mal":7.5,"imdb":7.2},
    {"t":"Miss Hokusai","y":2015,"d":"Keiichi Hara","cat":["historical","emotional_slice","music_art"],"mal":7.5,"imdb":7.2},
    {"t":"The Boy and the Beast","y":2015,"d":"Mamoru Hosoda","cat":["fantasy_adventure","action_epic","emotional_slice"],"mal":7.7,"imdb":7.3},
    {"t":"Psycho-Pass: The Movie","y":2015,"d":"Naoyoshi Shiotani","cat":["sci_fi","psychological","philosophical_surreal"],"mal":7.5,"imdb":7.1},
    {"t":"Attack on Titan: Chronicle","y":2020,"d":"Tetsuro Araki","cat":["action_epic","fantasy_adventure","philosophical_surreal"],"mal":8.5,"imdb":8.0},
    {"t":"The Anthem of the Heart","y":2015,"d":"Mari Okada","cat":["emotional_slice","romance_drama","music_art"],"mal":7.8,"imdb":7.4},
    {"t":"Mai Mai Miracle","y":2009,"d":"Sunao Katabuchi","cat":["emotional_slice","historical","fantasy_adventure"],"mal":7.3,"imdb":7.0},
    {"t":"Birthday Wonderland","y":2019,"d":"Keiichi Hara","cat":["fantasy_adventure","emotional_slice"],"mal":6.8,"imdb":6.5},
    {"t":"Mary and the Witchs Flower","y":2017,"d":"Hiromasa Yonebayashi","cat":["fantasy_adventure","emotional_slice"],"mal":7.1,"imdb":6.8},
    {"t":"Mirai","y":2018,"d":"Mamoru Hosoda","cat":["fantasy_adventure","emotional_slice"],"mal":7.3,"imdb":7.0},
    {"t":"Modest Heroes","y":2018,"d":"Studio Ponoc","cat":["emotional_slice","short_film"],"mal":6.8,"imdb":6.5},
    {"t":"Wreck-It Ralph","y":2012,"d":"Rich Moore","cat":["comedy_satirical","action_epic"],"mal":7.5,"imdb":7.1},

    # --- 2015-2020 ---
    {"t":"The Night Is Short, Walk on Girl","y":2017,"d":"Masaaki Yuasa","cat":["comedy_satirical","romance_drama","philosophical_surreal"],"mal":8.05,"imdb":7.6},
    {"t":"Lu Over the Wall","y":2017,"d":"Masaaki Yuasa","cat":["fantasy_adventure","emotional_slice"],"mal":7.1,"imdb":6.8},
    {"t":"Ride Your Wave","y":2019,"d":"Masaaki Yuasa","cat":["romance_drama","emotional_slice","fantasy_adventure"],"mal":7.45,"imdb":7.0},
    {"t":"Liz and the Blue Bird","y":2018,"d":"Naoko Yamada","cat":["emotional_slice","music_art","romance_drama"],"mal":8.1,"imdb":7.6},
    {"t":"Violet Evergarden: The Movie","y":2020,"d":"Taichi Ishidate","cat":["emotional_slice","romance_drama"],"mal":8.5,"imdb":8.1},
    {"t":"Promare","y":2019,"d":"Hiroyuki Imaishi","cat":["action_epic","sci_fi","comedy_satirical"],"mal":7.8,"imdb":7.1},
    {"t":"Ride Your Wave","y":2019,"d":"Masaaki Yuasa","cat":["romance_drama","emotional_slice"],"mal":7.45,"imdb":7.0},
    {"t":"Children of the Sea","y":2019,"d":"Ayumu Watanabe","cat":["philosophical_surreal","fantasy_adventure","emotional_slice"],"mal":7.1,"imdb":6.8},
    {"t":"Weathering with You","y":2019,"d":"Makoto Shinkai","cat":["romance_drama","fantasy_adventure","emotional_slice"],"mal":8.26,"imdb":7.5},
    {"t":"The First Slam Dunk","y":2022,"d":"Takehiko Inoue","cat":["sports","emotional_slice","action_epic"],"mal":8.5,"imdb":8.0},

    # --- 2020-2026 ---
    {"t":"Jujutsu Kaisen 0","y":2021,"d":"Seong-Hu Park","cat":["action_epic","fantasy_adventure"],"mal":8.5,"imdb":7.8},
    {"t":"One Piece Film: Red","y":2022,"d":"Goro Taniguchi","cat":["action_epic","music_art","fantasy_adventure"],"mal":7.5,"imdb":7.0},
    {"t":"Suzume","y":2022,"d":"Makoto Shinkai","cat":["fantasy_adventure","emotional_slice","action_epic"],"mal":8.35,"imdb":7.6},
    {"t":"Belle","y":2021,"d":"Mamoru Hosoda","cat":["fantasy_adventure","music_art","emotional_slice"],"mal":7.65,"imdb":7.2},
    {"t":"Inu-Oh","y":2021,"d":"Masaaki Yuasa","cat":["music_art","historical","philosophical_surreal"],"mal":7.6,"imdb":7.2},
    {"t":"The Boy and the Heron","y":2023,"d":"Hayao Miyazaki","cat":["fantasy_adventure","philosophical_surreal","emotional_slice"],"mal":7.66,"imdb":7.4},
    {"t":"Spy x Family Code: White","y":2023,"d":"Takashi Katagiri","cat":["action_epic","comedy_satirical"],"mal":7.5,"imdb":7.0},
    {"t":"Digimon Adventure: Last Evolution Kizuna","y":2020,"d":"Tomohisa Taguchi","cat":["action_epic","emotional_slice"],"mal":7.8,"imdb":7.4},
    {"t":"Ranking of Kings: The Treasure Chest of Courage","y":2023,"y":2023,"d":"Shingo Kaneko","cat":["fantasy_adventure","emotional_slice"],"mal":7.2,"imdb":6.8},
    {"t":"Chainsaw Man: Reze Arc","y":2025,"d":"Tatsuya Yoshihara","cat":["action_epic","horror_thriller"],"mal":9.13,"imdb":8.5},
    {"t":"Mononoke the Movie: Phantom in the Rain","y":2024,"d":"Kenji Nakamura","cat":["horror_thriller","philosophical_surreal","historical"],"mal":7.8,"imdb":7.5},
    {"t":"The Colors Within","y":2024,"d":"Naoko Yamada","cat":["emotional_slice","music_art"],"mal":7.7,"imdb":7.3},
    {"t":"Sailor Moon Cosmos Part 1","y":2024,"d":"Kazuko Tadano","cat":["fantasy_adventure","romance_drama"],"mal":7.5,"imdb":7.0},
    {"t":"Sailor Moon Cosmos Part 2","y":2024,"d":"Kazuko Tadano","cat":["fantasy_adventure","romance_drama"],"mal":7.5,"imdb":7.0},
    {"t":"Look Back","y":2024,"d":"Kiyotaka Oshiyama","cat":["emotional_slice","short_film"],"mal":8.5,"imdb":8.0},
    {"t":"Totto-chan: The Little Girl at the Window","y":2023,"d":"Shinnosuke Yakuwa","cat":["emotional_slice","historical"],"mal":7.2,"imdb":6.8},
    {"t":"The Imaginary","y":2023,"d":"Yoshiyuki Momose","cat":["fantasy_adventure","emotional_slice"],"mal":7.5,"imdb":7.1},
    {"t":"Nimona","y":2023,"d":"Nick Bruno","cat":["action_epic","comedy_satirical"],"mal":7.8,"imdb":7.3},

    # --- EKSTRA FİLMLER (genişletilmiş liste) ---
    {"t":"Appleseed","y":2004,"d":"Shinji Aramaki","cat":["sci_fi","cyberpunk","action_epic"],"mal":6.8,"imdb":6.5},
    {"t":"Appleseed: Ex Machina","y":2007,"d":"Shinji Aramaki","cat":["sci_fi","cyberpunk"],"mal":6.5,"imdb":6.2},
    {"t":"Appleseed Alpha","y":2014,"d":"Shinji Aramaki","cat":["sci_fi","cyberpunk"],"mal":6.2,"imdb":5.9},
    {"t":"Blade Runner: Black Out 2022","y":2017,"d":"Shinichiro Watanabe","cat":["sci_fi","cyberpunk"],"mal":6.8,"imdb":6.5},
    {"t":"Burn the Witch","y":2020,"d":"Tatsuro Koishi","cat":["action_epic","fantasy_adventure"],"mal":6.5,"imdb":6.2},
    {"t":"Dragon Ball Z: Broly – The Legendary Super Saiyan","y":1993,"d":"Shigeyasu Yamauchi","cat":["action_epic"],"mal":7.2,"imdb":6.9},
    {"t":"Dragon Ball Z: Broly – Second Coming","y":1994,"d":"Shigeyasu Yamauchi","cat":["action_epic"],"mal":6.8,"imdb":6.5},
    {"t":"Dragon Ball Z: Bio-Broly","y":1994,"d":"Yoshihiro Ueda","cat":["action_epic"],"mal":6.2,"imdb":5.9},
    {"t":"Dragon Ball Z: Fusion Reborn","y":1995,"d":"Shigeyasu Yamauchi","cat":["action_epic"],"mal":7.0,"imdb":6.7},
    {"t":"Dragon Ball Z: Wrath of the Dragon","y":1995,"d":"Mitsuo Hashimoto","cat":["action_epic"],"mal":6.8,"imdb":6.5},
    {"t":"Dragon Ball Z: Battle of Gods","y":2013,"d":"Masahiro Hosoda","cat":["action_epic","comedy_satirical"],"mal":7.4,"imdb":7.0},
    {"t":"Dragon Ball Z: Resurrection F","y":2015,"d":"Tadayoshi Yamamuro","cat":["action_epic"],"mal":7.2,"imdb":6.8},
    {"t":"Dragon Ball Super: Broly","y":2018,"d":"Tadayoshi Yamamuro","cat":["action_epic"],"mal":8.1,"imdb":7.8},
    {"t":"Dragon Ball Super: Super Hero","y":2022,"d":"Tadayoshi Yamamuro","cat":["action_epic","comedy_satirical"],"mal":7.5,"imdb":7.1},
    {"t":"Oban Star-Racers","y":2006,"d":"Savin Yeatman-Eiffel","cat":["sci_fi","action_epic","sports"],"mal":7.2,"imdb":6.9},
    {"t":"Kingsglaive: Final Fantasy XV","y":2016,"d":"Takeshi Nozue","cat":["action_epic","fantasy_adventure"],"mal":7.0,"imdb":6.7},
    {"t":"Kingsglaive: Final Fantasy XV","y":2016,"d":"Takeshi Nozue","cat":["action_epic","fantasy_adventure"],"mal":7.0,"imdb":6.7},
    {"t":"Final Fantasy VII: Advent Children","y":2005,"d":"Tetsuya Nomura","cat":["action_epic","sci_fi"],"mal":7.2,"imdb":6.9},
    {"t":"Space Pirate Captain Harlock","y":2013,"d":"Shinji Aramaki","cat":["sci_fi","action_epic"],"mal":6.5,"imdb":6.2},
    {"t":"Gantz:O","y":2016,"d":"Yasushi Kawamura","cat":["action_epic","sci_fi","horror_thriller"],"mal":7.2,"imdb":6.9},
    {"t":"Inuyasha: Affections Touching Across Time","y":2001,"d":"Toshiya Shinohara","cat":["action_epic","fantasy_adventure","romance_drama"],"mal":7.2,"imdb":6.9},
    {"t":"Inuyasha: The Castle Beyond the Looking Glass","y":2002,"d":"Toshiya Shinohara","cat":["action_epic","fantasy_adventure"],"mal":7.3,"imdb":7.0},
    {"t":"Inuyasha: Swords of an Honorable Ruler","y":2003,"d":"Toshiya Shinohara","cat":["action_epic","fantasy_adventure"],"mal":7.4,"imdb":7.1},
    {"t":"Inuyasha: Fire on the Mystic Island","y":2004,"d":"Toshiya Shinohara","cat":["action_epic","fantasy_adventure"],"mal":7.0,"imdb":6.7},
    {"t":"In This Corner of the World: Sincerely Yours","y":2019,"d":"Sunao Katabuchi","cat":["historical","emotional_slice"],"mal":7.2,"imdb":6.8},
    {"t":"The Kingdom of Dreams and Madness","y":2013,"d":"Mami Sunada","cat":["music_art","emotional_slice"],"mal":7.5,"imdb":7.2},
    {"t":"The Tale of the Princess Kaguya","y":2013,"d":"Isao Takahata","cat":["fantasy_adventure","emotional_slice","historical"],"mal":8.1,"imdb":8.0},
    {"t":"Only Yesterday","y":1991,"d":"Isao Takahata","cat":["emotional_slice","romance_drama"],"mal":7.94,"imdb":7.6},
    {"t":"Pom Poko","y":1994,"d":"Isao Takahata","cat":["fantasy_adventure","comedy_satirical"],"mal":7.1,"imdb":7.3},
    {"t":"My Neighbors the Yamadas","y":1999,"d":"Isao Takahata","cat":["comedy_satirical","emotional_slice"],"mal":7.33,"imdb":7.1},
    {"t":"The Red Turtle","y":2016,"d":"Michael Dudok de Wit","cat":["emotional_slice","fantasy_adventure","short_film"],"mal":7.5,"imdb":7.2},
    {"t":"The Red Spectacles","y":1987,"d":"Mamoru Oshii","cat":["philosophical_surreal","action_epic"],"mal":6.8,"imdb":6.5},
    {"t":"StrayDog: Kerberos Panzer Cops","y":1991,"d":"Mamoru Oshii","cat":["action_epic","sci_fi"],"mal":7.1,"imdb":6.8},
    {"t":"Talking Head","y":1992,"d":"Mamoru Oshii","cat":["mystery","philosophical_surreal"],"mal":6.8,"imdb":6.5},
    {"t":"Avalon","y":2001,"d":"Mamoru Oshii","cat":["sci_fi","cyberpunk","philosophical_surreal"],"mal":6.95,"imdb":6.5},
    {"t":"Tachigui: The Amazing Lives of the Fast Food Grifters","y":2006,"d":"Mamoru Oshii","cat":["comedy_satirical","philosophical_surreal"],"mal":6.5,"imdb":6.2},
    {"t":"Shin Godzilla","y":2016,"d":"Hideaki Anno","cat":["sci_fi","action_epic"],"mal":7.8,"imdb":7.1},
    {"t":"Shin Ultraman","y":2022,"d":"Hideaki Anno","cat":["sci_fi","action_epic"],"mal":7.5,"imdb":6.8},
    {"t":"Shin Kamen Rider","y":2023,"d":"Hideaki Anno","cat":["action_epic","sci_fi"],"mal":7.2,"imdb":6.5},
    {"t":"Garden of Sinners: Overlooking View","y":2007,"d":"Eiichi Takahashi","cat":["mystery","horror_thriller","philosophical_surreal"],"mal":7.5,"imdb":7.1},
    {"t":"Garden of Sinners: Remaining Sense of Pain","y":2008,"d":"Takahiro Miura","cat":["mystery","horror_thriller"],"mal":7.4,"imdb":7.0},
    {"t":"Garden of Sinners: The Hollow Shrine","y":2008,"d":"Takahiro Miura","cat":["mystery","philosophical_surreal"],"mal":7.3,"imdb":6.9},
    {"t":"Garden of Sinners: Paradox Spiral","y":2008,"d":"Shinsuke Takizawa","cat":["mystery","horror_thriller","philosophical_surreal"],"mal":7.6,"imdb":7.2},
    {"t":"Garden of Sinners: The Hollow Garden","y":2008,"d":"Takahiro Miura","cat":["mystery","philosophical_surreal"],"mal":7.2,"imdb":6.8},
    {"t":"Fate/stay night: Heaven's Feel I. presage flower","y":2017,"d":"Tomonori Sudo","cat":["action_epic","fantasy_adventure","romance_drama"],"mal":8.0,"imdb":7.5},
    {"t":"Fate/stay night: Heaven's Feel II. lost butterfly","y":2019,"d":"Tomonori Sudo","cat":["action_epic","fantasy_adventure","romance_drama"],"mal":8.2,"imdb":7.7},
    {"t":"Fate/stay night: Heaven's Feel III. spring song","y":2020,"d":"Tomonori Sudo","cat":["action_epic","fantasy_adventure","romance_drama"],"mal":8.3,"imdb":7.8},
    {"t":"Demon Slayer: Mugen Train","y":2020,"d":"Haruo Sotozaki","cat":["action_epic","fantasy_adventure","emotional_slice"],"mal":8.5,"imdb":8.2},
    {"t":"Demon Slayer: To the Swordsmith Village","y":2023,"d":"Haruo Sotozaki","cat":["action_epic","fantasy_adventure"],"mal":7.2,"imdb":6.8},
    {"t":"Demon Slayer: To the Hashira Training","y":2024,"d":"Haruo Sotozaki","cat":["action_epic","fantasy_adventure"],"mal":7.0,"imdb":6.5},
    {"t":"One Piece Film: Strong World","y":2009,"d":"Munehisa Sakai","cat":["action_epic","fantasy_adventure"],"mal":7.5,"imdb":7.1},
    {"t":"One Piece Film: Gold","y":2016,"d":"Hiroaki Miyamoto","cat":["action_epic","fantasy_adventure"],"mal":7.4,"imdb":7.0},
    {"t":"One Piece: Stampede","y":2019,"d":"Takashi Otsuka","cat":["action_epic","fantasy_adventure"],"mal":7.8,"imdb":7.3},
    {"t":"Sailor Moon R: The Movie","y":1993,"d":"Kunihiko Ikuhara","cat":["fantasy_adventure","romance_drama"],"mal":7.2,"imdb":6.8},
    {"t":"Sailor Moon S: The Movie","y":1994,"d":"Hiroki Shibata","cat":["fantasy_adventure","romance_drama"],"mal":7.0,"imdb":6.7},
    {"t":"Sailor Moon SuperS: The Movie","y":1995,"d":"Hiroki Shibata","cat":["fantasy_adventure","romance_drama"],"mal":6.8,"imdb":6.5},
    {"t":"Sailor Moon Eternal Part 1","y":2021,"d":"Chiaki Kon","cat":["fantasy_adventure","romance_drama"],"mal":7.3,"imdb":6.8},
    {"t":"Sailor Moon Eternal Part 2","y":2021,"d":"Chiaki Kon","cat":["fantasy_adventure","romance_drama"],"mal":7.3,"imdb":6.8},
    {"t":"Digimon Adventure: Our War Game!","y":2000,"d":"Mamoru Hosoda","cat":["action_epic","sci_fi"],"mal":7.5,"imdb":7.1},
    {"t":"Digimon Adventure 02: Revenge of Diaboromon","y":2001,"d":"Jeff Nimoy","cat":["action_epic","sci_fi"],"mal":6.8,"imdb":6.5},
    {"t":"Digimon Tamers: Battle of Adventurers","y":2001,"d":"Tetsuo Imazawa","cat":["action_epic","sci_fi"],"mal":6.7,"imdb":6.4},
    {"t":"Digimon Tamers: Runaway Locomon","y":2002,"d":"Tetsuo Imazawa","cat":["action_epic","sci_fi"],"mal":6.5,"imdb":6.2},
    {"t":"Digimon Frontier: Island of Lost Digimon","y":2002,"d":"Takahiro Imamura","cat":["action_epic","sci_fi"],"mal":6.5,"imdb":6.2},
    {"t":"Digimon Adventure tri. Chapter 1: Reunion","y":2015,"d":"Keitaro Motonaga","cat":["action_epic","emotional_slice"],"mal":7.0,"imdb":6.5},
    {"t":"Digimon Adventure tri. Chapter 2: Determination","y":2016,"d":"Keitaro Motonaga","cat":["action_epic","emotional_slice"],"mal":6.8,"imdb":6.3},
    {"t":"Digimon Adventure tri. Chapter 3: Confession","y":2016,"d":"Keitaro Motonaga","cat":["action_epic","emotional_slice"],"mal":6.7,"imdb":6.2},
    {"t":"Digimon Adventure tri. Chapter 4: Loss","y":2017,"d":"Keitaro Motonaga","cat":["action_epic","emotional_slice"],"mal":6.8,"imdb":6.3},
    {"t":"Digimon Adventure tri. Chapter 5: Coexistence","y":2017,"d":"Keitaro Motonaga","cat":["action_epic","emotional_slice"],"mal":6.7,"imdb":6.2},
    {"t":"Digimon Adventure tri. Chapter 6: Future","y":2018,"d":"Keitaro Motonaga","cat":["action_epic","emotional_slice"],"mal":7.0,"imdb":6.5},
    {"t":"My Hero Academia: Two Heroes","y":2018,"d":"Kenji Nagasaki","cat":["action_epic","comedy_satirical"],"mal":7.8,"imdb":7.4},
    {"t":"My Hero Academia: Heroes Rising","y":2019,"d":"Kenji Nagasaki","cat":["action_epic","emotional_slice"],"mal":7.9,"imdb":7.5},
    {"t":"My Hero Academia: World Heroes Mission","y":2021,"d":"Kenji Nagasaki","cat":["action_epic"],"mal":7.5,"imdb":7.1},
    {"t":"Sword Art Online: Ordinal Scale","y":2017,"d":"Tomohiko Ito","cat":["action_epic","sci_fi","fantasy_adventure"],"mal":7.2,"imdb":6.8},
    {"t":"Sword Art Online: Progressive - Aria of a Starless Night","y":2021,"d":"Ayako Kouno","cat":["action_epic","romance_drama","sci_fi"],"mal":7.5,"imdb":7.1},
    {"t":"Sword Art Online: Progressive - Scherzo of Deep Night","y":2022,"d":"Ayako Kouno","cat":["action_epic","romance_drama","sci_fi"],"mal":7.3,"imdb":6.9},
    {"t":"Re:Zero -Starting Life in Another World- Memory Snow","y":2018,"d":"Masaharu Watanabe","cat":["fantasy_adventure","romance_drama"],"mal":7.5,"imdb":7.0},
    {"t":"Bofuri: I Don't Want to Get Hurt, so I'll Max Out My Defense.","y":2021,"d":"Yoshitsugu Kimura","cat":["comedy_satirical","fantasy_adventure"],"mal":7.0,"imdb":6.5},
    {"t":"Horimiya: The Missing Pieces","y":2023,"d":"Masashi Ishihama","cat":["romance_drama","comedy_satirical"],"mal":7.5,"imdb":7.0},
    {"t":"Tokyo Ghoul: Jack","y":2015,"d":"Shuhei Morita","cat":["action_epic","horror_thriller"],"mal":6.8,"imdb":6.5},
    {"t":"Rurouni Kenshin: The Motion Picture","y":1997,"d":"Kazuhiro Furuhashi","cat":["action_epic","historical"],"mal":7.2,"imdb":6.8},
    {"t":"Rurouni Kenshin: The Beginning","y":2021,"d":"Keishi Otomo","cat":["action_epic","historical","emotional_slice"],"mal":8.2,"imdb":7.8},
    {"t":"Vampire Hunter D","y":1985,"d":"Toyoo Ashida","cat":["horror_thriller","fantasy_adventure"],"mal":7.2,"imdb":6.9},
    {"t":"Wicked City","y":1987,"d":"Yoshiaki Kawajiri","cat":["horror_thriller","action_epic","cyberpunk"],"mal":7.0,"imdb":6.7},
    {"t":"Demon City Shinjuku","y":1988,"d":"Yoshiaki Kawajiri","cat":["horror_thriller","action_epic","cyberpunk"],"mal":6.8,"imdb":6.5},
    {"t":"The Five Star Stories","y":1989,"d":"Kazuo Yamazaki","cat":["sci_fi","action_epic","mecha"],"mal":6.5,"imdb":6.2},
    {"t":"Cyber City Oedo 808","y":1990,"d":"Yoshiaki Kawajiri","cat":["cyberpunk","action_epic","horror_thriller"],"mal":7.0,"imdb":6.7},
    {"t":"Doomed Megalopolis","y":1991,"d":"Rintaro","cat":["horror_thriller","sci_fi","historical"],"mal":6.8,"imdb":6.5},
    {"t":"Spirit of Wonder","y":1992,"d":"Takashi Anno","cat":["sci_fi","fantasy_adventure"],"mal":6.5,"imdb":6.2},
    {"t":"Catnapped!","y":1995,"d":"Takashi Anno","cat":["fantasy_adventure","comedy_satirical"],"mal":6.2,"imdb":5.9},
    {"t":"Spring and Chaos","y":1996,"d":"Shoji Kawamori","cat":["historical","emotional_slice"],"mal":6.5,"imdb":6.2},
    {"t":"Princess Arete","y":2001,"d":"Sunao Katabuchi","cat":["fantasy_adventure","emotional_slice"],"mal":7.0,"imdb":6.7},
    {"t":"The Place Promised in Our Early Days","y":2004,"d":"Makoto Shinkai","cat":["sci_fi","romance_drama","emotional_slice"],"mal":7.02,"imdb":6.9},
    {"t":"Voices of a Distant Star","y":2002,"d":"Makoto Shinkai","cat":["sci_fi","romance_drama","emotional_slice"],"mal":7.18,"imdb":7.2},
    {"t":"She and Her Cat","y":1999,"d":"Makoto Shinkai","cat":["emotional_slice","short_film"],"mal":7.15,"imdb":7.0},
    {"t":"Ninja Scroll","y":1993,"d":"Yoshiaki Kawajiri","cat":["action_epic","historical","horror_thriller"],"mal":7.5,"imdb":7.4},
    {"t":"Vampire Hunter D: Bloodlust","y":2000,"d":"Yoshiaki Kawajiri","cat":["horror_thriller","action_epic","fantasy_adventure"],"mal":7.6,"imdb":7.4},
    {"t":"Highlander: The Search for Vengeance","y":2007,"d":"Yoshiaki Kawajiri","cat":["action_epic","fantasy_adventure"],"mal":6.8,"imdb":6.5},
    {"t":"Afro Samurai: Resurrection","y":2009,"d":"Fuminori Kizaki","cat":["action_epic","historical"],"mal":6.5,"imdb":6.2},
    {"t":"The Tibetan Dog","y":2011,"d":"Masayuki Kojima","cat":["emotional_slice","fantasy_adventure"],"mal":6.8,"imdb":6.5},
    {"t":"The Life of Budori Gusuko","y":2012,"d":"Gisaburo Sugii","cat":["fantasy_adventure","emotional_slice"],"mal":6.5,"imdb":6.2},
    {"t":"Patema Inverted","y":2013,"d":"Yasuhiro Yoshiura","cat":["sci_fi","fantasy_adventure","romance_drama"],"mal":7.5,"imdb":7.1},
    {"t":"Time of Eve: The Movie","y":2010,"d":"Yasuhiro Yoshiura","cat":["sci_fi","philosophical_surreal","emotional_slice"],"mal":7.5,"imdb":7.1},
    {"t":"Harmony","y":2015,"d":"Michael Arias","cat":["sci_fi","philosophical_surreal"],"mal":7.2,"imdb":6.8},
    {"t":"Genocidal Organ","y":2017,"d":"Shukou Murase","cat":["sci_fi","philosophical_surreal","action_epic"],"mal":6.8,"imdb":6.5},
    {"t":"Napping Princess","y":2017,"d":"Kenji Kamiyama","cat":["sci_fi","fantasy_adventure"],"mal":6.8,"imdb":6.5},
    {"t":"Lu Over the Wall","y":2017,"d":"Masaaki Yuasa","cat":["fantasy_adventure","emotional_slice"],"mal":7.1,"imdb":6.8},
    {"t":"The Night Is Short, Walk on Girl","y":2017,"d":"Masaaki Yuasa","cat":["comedy_satirical","romance_drama","philosophical_surreal"],"mal":8.05,"imdb":7.6},
    {"t":"Ride Your Wave","y":2019,"d":"Masaaki Yuasa","cat":["romance_drama","emotional_slice","fantasy_adventure"],"mal":7.45,"imdb":7.0},
    {"t":"Inu-Oh","y":2021,"d":"Masaaki Yuasa","cat":["music_art","historical","philosophical_surreal"],"mal":7.6,"imdb":7.2},
    {"t":"Penguin Highway","y":2018,"d":"Hiroyasu Ishida","cat":["sci_fi","fantasy_adventure","emotional_slice"],"mal":7.2,"imdb":6.9},
    {"t":"Josee, the Tiger and the Fish","y":2020,"d":"Kotaro Tamura","cat":["romance_drama","emotional_slice"],"mal":7.5,"imdb":7.1},
    {"t":"Fortune Favors Lady Nikuko","y":2021,"d":"Ayumu Watanabe","cat":["emotional_slice","comedy_satirical"],"mal":6.8,"imdb":6.5},
    {"t":"The House of the Lost on the Cape","y":2021,"d":"Shinichiro Watanabe","cat":["fantasy_adventure","emotional_slice"],"mal":6.5,"imdb":6.2},
    {"t":"Totto-chan: The Little Girl at the Window","y":2023,"d":"Shinnosuke Yakuwa","cat":["emotional_slice","historical"],"mal":7.2,"imdb":6.8},
    {"t":"The Imaginary","y":2023,"d":"Yoshiyuki Momose","cat":["fantasy_adventure","emotional_slice"],"mal":7.5,"imdb":7.1},
    {"t":"Look Back","y":2024,"d":"Kiyotaka Oshiyama","cat":["emotional_slice","short_film"],"mal":8.5,"imdb":8.0},
    {"t":"Mononoke the Movie: Phantom in the Rain","y":2024,"d":"Kenji Nakamura","cat":["horror_thriller","philosophical_surreal","historical"],"mal":7.8,"imdb":7.5},
    {"t":"The Colors Within","y":2024,"d":"Naoko Yamada","cat":["emotional_slice","music_art"],"mal":7.7,"imdb":7.3},
    {"t":"Sailor Moon Cosmos Part 1","y":2024,"d":"Kazuko Tadano","cat":["fantasy_adventure","romance_drama"],"mal":7.5,"imdb":7.0},
    {"t":"Sailor Moon Cosmos Part 2","y":2024,"d":"Kazuko Tadano","cat":["fantasy_adventure","romance_drama"],"mal":7.5,"imdb":7.0},
    {"t":"Chainsaw Man: Reze Arc","y":2025,"d":"Tatsuya Yoshihara","cat":["action_epic","horror_thriller"],"mal":9.13,"imdb":8.5},
    {"t":"Madoka Magica: The Movie – Walpurgisnacht: Rising","y":2025,"d":"Akiyuki Shinbo","cat":["philosophical_surreal","fantasy_adventure","action_epic"],"mal":8.5,"imdb":8.0},
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
    key = f"{f.get('t', f.get('title','')).lower()}_{f.get('y', f.get('year',2000))}"
    if key not in seen:
        seen.add(key)
        unique.append(f)

# İzlenenleri çıkar
filtered = [f for f in unique if not is_watched(f["t"])]
print(f"Toplam film: {len(unique)}")
print(f"Izlenen cikarildi: {len(unique)-len(filtered)}")
print(f"Kalani: {len(filtered)}")

# Analiz üret
analyzed = []
for f in filtered:
    mal = f.get("mal", 7.0)
    imdb = f.get("imdb", 0)
    cats = f.get("cat", [])
    year = f.get("y", 2000)
    title = f.get("t", f.get("title", ""))
    
    analyzed.append({
        "title": title,
        "year": year,
        "director": f.get("d", ""),
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
    for i,f in enumerate(analyzed[:20],1):
        f.write(f"  {i:2d}. {f['title']} ({f['year']}) OWL:{f['owl_score']:.1f}\n")
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
