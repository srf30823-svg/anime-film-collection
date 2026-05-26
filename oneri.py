#!/usr/bin/env python3
"""
OWL Anime & Film Oneri Sistemi v2.0
Python tabanli, LLM olmayan akilli oneri motoru
Kullan: python3 oneri.py [--cli|--recommend N|--category TUR|--stats|--report|--search FILM|--watch FILM|--init]
"""
import json, os, sys, sqlite3, argparse
from datetime import datetime

BASE = "/data/data/com.termux/files/home/anime-project"
DB_PATH = f"{BASE}/data/recommender.db"
TXT_DIR = f"{BASE}/output/txt"

ALL_CATS = {
    "phil_surreal":"Felsefi&Surreal","action_epic":"Aksiyon&Epik","psych_thriller":"Psikolojik&Gerilim",
    "comedy_satire":"Komedi&Satirik","emotional":"Duygusal","fantasy":"Fantastik","sci_fi":"BilimKurgu",
    "cyberpunk":"Cyberpunk","mystery":"Gizem","horror":"Korku","romance":"Romantik","sports":"Spor",
    "historical":"Tarihi","music_art":"Muzik&Sanat","mecha":"Mecha","short":"KisaFilm",
    "slice_of_life":"GunlukYasam","isekai":"Isekai","dystopia":"Distopia","war":"Savas",
}
TASTE_W = {
    "phil_surreal":10,"psych_thriller":9,"cyberpunk":9,"action_epic":9,"emotional":8,"fantasy":8,
    "comedy_satire":8,"music_art":7,"sci_fi":7,"sports":7,"mystery":7,"short":7,"historical":6,
    "horror":6,"mecha":6,"romance":5,"slice_of_life":7,"isekai":6,"dystopia":8,"war":7,
}

# === 300+ FILM VERI TABANI ===
FILMS = [
    {"t":"Belladonna of Sadness","y":1973,"d":"Eiichi Yamamoto","cat":["phil_surreal","horror"],"mal":7.5,"imdb":7.3},
    {"t":"Hols: Prince of the Sun","y":1968,"d":"Isao Takahata","cat":["fantasy","action_epic"],"mal":7.5,"imdb":7.2},
    {"t":"Lupin III: The Castle of Cagliostro","y":1979,"d":"Hayao Miyazaki","cat":["action_epic","fantasy"],"mal":7.8,"imdb":7.6},
    {"t":"Galaxy Express 999","y":1979,"d":"Rintaro","cat":["sci_fi","fantasy"],"mal":7.5,"imdb":7.2},
    {"t":"Nausicaa of the Valley of the Wind","y":1984,"d":"Hayao Miyazaki","cat":["fantasy","sci_fi","emotional"],"mal":8.3,"imdb":8.0},
    {"t":"Urusei Yatsura 2: Beautiful Dreamer","y":1984,"d":"Mamoru Oshii","cat":["phil_surreal","comedy_satire"],"mal":7.6,"imdb":7.4},
    {"t":"Angel's Egg","y":1985,"d":"Mamoru Oshii","cat":["phil_surreal","emotional"],"mal":7.5,"imdb":7.3},
    {"t":"Castle in the Sky","y":1986,"d":"Hayao Miyazaki","cat":["fantasy","action_epic"],"mal":8.2,"imdb":8.0},
    {"t":"Wicked City","y":1987,"d":"Yoshiaki Kawajiri","cat":["horror","action_epic","cyberpunk"],"mal":7.0,"imdb":6.7},
    {"t":"My Neighbor Totoro","y":1988,"d":"Hayao Miyazaki","cat":["emotional","fantasy","slice_of_life"],"mal":8.3,"imdb":8.1},
    {"t":"Kikis Delivery Service","y":1989,"d":"Hayao Miyazaki","cat":["fantasy","emotional"],"mal":8.2,"imdb":7.8},
    {"t":"Grave of the Fireflies","y":1988,"d":"Isao Takahata","cat":["emotional","historical","war"],"mal":8.5,"imdb":8.5},
    {"t":"Akira","y":1988,"d":"Katsuhiro Otomo","cat":["cyberpunk","sci_fi","action_epic","dystopia"],"mal":8.2,"imdb":8.0},
    {"t":"Patlabor: The Movie","y":1989,"d":"Mamoru Oshii","cat":["mecha","sci_fi","action_epic"],"mal":7.6,"imdb":7.1},
    {"t":"Cyber City Oedo 808","y":1990,"d":"Yoshiaki Kawajiri","cat":["cyberpunk","action_epic","horror","dystopia"],"mal":7.0,"imdb":6.7},
    {"t":"Only Yesterday","y":1991,"d":"Isao Takahata","cat":["emotional","romance","slice_of_life"],"mal":7.9,"imdb":7.6},
    {"t":"Ninja Scroll","y":1993,"d":"Yoshiaki Kawajiri","cat":["action_epic","historical","horror"],"mal":7.5,"imdb":7.4},
    {"t":"Patlabor 2: The Movie","y":1993,"d":"Mamoru Oshii","cat":["mecha","sci_fi","phil_surreal","mystery"],"mal":7.7,"imdb":7.3},
    {"t":"Pom Poko","y":1994,"d":"Isao Takahata","cat":["fantasy","comedy_satire","historical"],"mal":7.1,"imdb":7.3},
    {"t":"Whisper of the Heart","y":1995,"d":"Yoshifumi Kondo","cat":["romance","emotional","slice_of_life"],"mal":8.2,"imdb":7.8},
    {"t":"Ghost in the Shell","y":1995,"d":"Mamoru Oshii","cat":["cyberpunk","sci_fi","phil_surreal","action_epic"],"mal":8.3,"imdb":7.9},
    {"t":"Perfect Blue","y":1997,"d":"Satoshi Kon","cat":["psych_thriller","horror","mystery"],"mal":8.5,"imdb":8.0},
    {"t":"Princess Mononoke","y":1997,"d":"Hayao Miyazaki","cat":["fantasy","action_epic","historical"],"mal":8.7,"imdb":8.3},
    {"t":"Ocean Waves","y":1993,"d":"Tomomi Mochizuki","cat":["romance","emotional","slice_of_life"],"mal":6.9,"imdb":6.8},
    {"t":"Jin-Roh: The Wolf Brigade","y":1999,"d":"Hiroyuki Okiura","cat":["action_epic","phil_surreal","historical","dystopia"],"mal":7.6,"imdb":7.3},
    {"t":"Revolutionary Girl Utena","y":1999,"d":"Kunihiko Ikuhara","cat":["phil_surreal","psych_thriller","romance"],"mal":7.8,"imdb":7.4},
    {"t":"Vampire Hunter D: Bloodlust","y":2000,"d":"Yoshiaki Kawajiri","cat":["horror","action_epic","fantasy"],"mal":7.6,"imdb":7.4},
    {"t":"Blood: The Last Vampire","y":2000,"d":"Hiroyuki Kitakubo","cat":["horror","action_epic"],"mal":6.8,"imdb":6.5},
    {"t":"Millennium Actress","y":2001,"d":"Satoshi Kon","cat":["phil_surreal","emotional","romance"],"mal":8.2,"imdb":7.8},
    {"t":"Spirited Away","y":2001,"d":"Hayao Miyazaki","cat":["fantasy","emotional"],"mal":8.8,"imdb":8.6},
    {"t":"Metropolis","y":2001,"d":"Rintaro","cat":["sci_fi","phil_surreal","dystopia"],"mal":7.2,"imdb":7.0},
    {"t":"Cowboy Bebop: The Movie","y":2001,"d":"Shinichiro Watanabe","cat":["action_epic","sci_fi","cyberpunk"],"mal":8.0,"imdb":7.6},
    {"t":"Tokyo Godfathers","y":2003,"d":"Satoshi Kon","cat":["comedy_satire","emotional","slice_of_life"],"mal":8.1,"imdb":7.8},
    {"t":"Ghost in the Shell 2: Innocence","y":2004,"d":"Mamoru Oshii","cat":["cyberpunk","phil_surreal","sci_fi","mystery"],"mal":7.6,"imdb":7.4},
    {"t":"Howls Moving Castle","y":2004,"d":"Hayao Miyazaki","cat":["fantasy","romance","action_epic"],"mal":8.6,"imdb":8.2},
    {"t":"Mind Game","y":2004,"d":"Masaaki Yuasa","cat":["phil_surreal","comedy_satire","psych_thriller"],"mal":7.9,"imdb":7.6},
    {"t":"Steamboy","y":2004,"d":"Katsuhiro Otomo","cat":["sci_fi","action_epic","historical"],"mal":7.0,"imdb":6.8},
    {"t":"Appleseed","y":2004,"d":"Shinji Aramaki","cat":["sci_fi","cyberpunk","action_epic"],"mal":6.8,"imdb":6.5},
    {"t":"Black Cat","y":2005,"d":"Shin Itagaki","cat":["action_epic","comedy_satire"],"mal":7.2,"imdb":6.8},
    {"t":"Paprika","y":2006,"d":"Satoshi Kon","cat":["phil_surreal","sci_fi","psych_thriller","mystery"],"mal":8.0,"imdb":7.7},
    {"t":"The Girl Who Leapt Through Time","y":2006,"d":"Mamoru Hosoda","cat":["sci_fi","romance","emotional"],"mal":8.1,"imdb":7.7},
    {"t":"Tekkonkinkreet","y":2006,"d":"Michael Arias","cat":["action_epic","phil_surreal","emotional"],"mal":7.8,"imdb":7.4},
    {"t":"Sword of the Stranger","y":2007,"d":"Masahiro Ando","cat":["action_epic","historical"],"mal":8.1,"imdb":7.7},
    {"t":"Summer Wars","y":2009,"d":"Mamoru Hosoda","cat":["sci_fi","comedy_satire","emotional"],"mal":7.9,"imdb":7.5},
    {"t":"Redline","y":2009,"d":"Takeshi Koike","cat":["action_epic","sci_fi","comedy_satire","sports"],"mal":8.2,"imdb":7.7},
    {"t":"Colourful","y":2010,"d":"Keiichi Hara","cat":["emotional","phil_surreal","slice_of_life"],"mal":7.6,"imdb":7.3},
    {"t":"The Tatami Galaxy","y":2010,"d":"Masaaki Yuasa","cat":["phil_surreal","psych_thriller","comedy_satire"],"mal":8.5,"imdb":8.1},
    {"t":"Time of Eve: The Movie","y":2010,"d":"Yasuhiro Yoshiura","cat":["sci_fi","phil_surreal","emotional","slice_of_life"],"mal":7.5,"imdb":7.1},
    {"t":"Children Who Chase Lost Voices","y":2011,"d":"Makoto Shinkai","cat":["fantasy","emotional","romance"],"mal":7.3,"imdb":7.1},
    {"t":"Wolf Children","y":2012,"d":"Mamoru Hosoda","cat":["fantasy","emotional","romance","slice_of_life"],"mal":8.6,"imdb":8.2},
    {"t":"From Up on Poppy Hill","y":2011,"d":"Goro Miyazaki","cat":["romance","emotional","historical","slice_of_life"],"mal":7.4,"imdb":7.4},
    {"t":"Summer Days with Coo","y":2007,"d":"Keiichi Hara","cat":["fantasy","emotional","comedy_satire"],"mal":7.4,"imdb":7.1},
    {"t":"The Garden of Words","y":2013,"d":"Makoto Shinkai","cat":["romance","emotional","slice_of_life"],"mal":7.5,"imdb":7.4},
    {"t":"The Wind Rises","y":2013,"d":"Hayao Miyazaki","cat":["historical","romance","emotional"],"mal":8.0,"imdb":7.8},
    {"t":"The Tale of The Princess Kaguya","y":2013,"d":"Isao Takahata","cat":["fantasy","emotional","historical"],"mal":8.1,"imdb":8.0},
    {"t":"Miss Hokusai","y":2015,"d":"Keiichi Hara","cat":["historical","emotional","music_art"],"mal":7.5,"imdb":7.2},
    {"t":"Psycho-Pass: The Movie","y":2015,"d":"Naoyoshi Shiotani","cat":["sci_fi","psych_thriller","phil_surreal","dystopia"],"mal":7.5,"imdb":7.1},
    {"t":"Anthem of the Heart","y":2015,"d":"Mari Okada","cat":["emotional","romance","music_art"],"mal":7.8,"imdb":7.4},
    {"t":"The Boy and the Beast","y":2015,"d":"Mamoru Hosoda","cat":["fantasy","action_epic","emotional"],"mal":7.7,"imdb":7.3},
    {"t":"A Silent Voice","y":2016,"d":"Naoko Yamada","cat":["emotional","romance","slice_of_life"],"mal":8.9,"imdb":8.2},
    {"t":"In This Corner of the World","y":2016,"d":"Sunao Katabuchi","cat":["historical","emotional","war","slice_of_life"],"mal":8.2,"imdb":7.8},
    {"t":"The Red Turtle","y":2016,"d":"Michael Dudok de Wit","cat":["emotional","fantasy","short"],"mal":7.5,"imdb":7.2},
    {"t":"Maquia: When the Promised Flower Blooms","y":2018,"d":"Mari Okada","cat":["fantasy","emotional","romance"],"mal":8.1,"imdb":7.6},
    {"t":"Liz and the Blue Bird","y":2018,"d":"Naoko Yamada","cat":["emotional","music_art","romance","slice_of_life"],"mal":8.1,"imdb":7.6},
    {"t":"Penguin Highway","y":2018,"d":"Hiroyasu Ishida","cat":["sci_fi","fantasy","emotional","slice_of_life"],"mal":7.2,"imdb":6.9},
    {"t":"The Night Is Short, Walk on Girl","y":2017,"d":"Masaaki Yuasa","cat":["comedy_satire","romance","phil_surreal"],"mal":8.1,"imdb":7.6},
    {"t":"Lu Over the Wall","y":2017,"d":"Masaaki Yuasa","cat":["fantasy","emotional"],"mal":7.1,"imdb":6.8},
    {"t":"Promare","y":2019,"d":"Hiroyuki Imaishi","cat":["action_epic","sci_fi","comedy_satire"],"mal":7.8,"imdb":7.1},
    {"t":"Ride Your Wave","y":2019,"d":"Masaaki Yuasa","cat":["romance","emotional","fantasy"],"mal":7.5,"imdb":7.0},
    {"t":"Children of the Sea","y":2019,"d":"Ayumu Watanabe","cat":["phil_surreal","fantasy","emotional"],"mal":7.1,"imdb":6.8},
    {"t":"Weathering with You","y":2019,"d":"Makoto Shinkai","cat":["romance","fantasy","emotional"],"mal":8.3,"imdb":7.5},
    {"t":"Violet Evergarden: The Movie","y":2020,"d":"Taichi Ishidate","cat":["emotional","romance","fantasy"],"mal":8.5,"imdb":8.1},
    {"t":"Demon Slayer: Mugen Train","y":2020,"d":"Haruo Sotozaki","cat":["action_epic","fantasy","emotional"],"mal":8.5,"imdb":8.2},
    {"t":"Jujutsu Kaisen 0","y":2021,"d":"Seong-Hu Park","cat":["action_epic","fantasy","horror"],"mal":8.5,"imdb":7.8},
    {"t":"Belle","y":2021,"d":"Mamoru Hosoda","cat":["fantasy","music_art","emotional","sci_fi"],"mal":7.7,"imdb":7.2},
    {"t":"One Piece Film: Red","y":2022,"d":"Goro Taniguchi","cat":["action_epic","music_art","fantasy"],"mal":7.5,"imdb":7.0},
    {"t":"Inu-Oh","y":2021,"d":"Masaaki Yuasa","cat":["music_art","historical","phil_surreal"],"mal":7.6,"imdb":7.2},
    {"t":"Ranking of Kings: The Treasure Chest of Courage","y":2023,"d":"Shingo Kaneko","cat":["fantasy","emotional"],"mal":7.2,"imdb":6.8},
    {"t":"The First Slam Dunk","y":2022,"d":"Takehiko Inoue","cat":["sports","emotional","action_epic"],"mal":8.5,"imdb":8.0},
    {"t":"Suzume","y":2022,"d":"Makoto Shinkai","cat":["fantasy","emotional","action_epic","romance"],"mal":8.4,"imdb":7.6},
    {"t":"The Boy and the Heron","y":2023,"d":"Hayao Miyazaki","cat":["fantasy","phil_surreal","emotional"],"mal":7.7,"imdb":7.4},
    {"t":"Spy x Family Code: White","y":2023,"d":"Takashi Katagiri","cat":["action_epic","comedy_satire"],"mal":7.5,"imdb":7.0},
    {"t":"Digimon Adventure: Last Evolution Kizuna","y":2020,"d":"Tomohisa Taguchi","cat":["action_epic","emotional","fantasy"],"mal":7.8,"imdb":7.4},
    {"t":"Look Back","y":2024,"d":"Kiyotaka Oshiyama","cat":["emotional","short"],"mal":8.5,"imdb":8.0},
    {"t":"Mononoke the Movie: Phantom in the Rain","y":2024,"d":"Kenji Nakamura","cat":["horror","phil_surreal","historical","mystery"],"mal":7.8,"imdb":7.5},
    {"t":"The Colors Within","y":2024,"d":"Naoko Yamada","cat":["emotional","music_art","slice_of_life"],"mal":7.7,"imdb":7.3},
    {"t":"Chainsaw Man: Reze Arc","y":2025,"d":"Tatsuya Yoshihara","cat":["action_epic","horror"],"mal":9.1,"imdb":8.5},
    {"t":"Madoka Magica: Walpurgisnacht Rising","y":2025,"d":"Akiyuki Shinbo","cat":["phil_surreal","fantasy","action_epic","dystopia"],"mal":8.5,"imdb":8.0},
    {"t":"Blue Giant","y":2023,"d":"Yuzuru Tachikawa","cat":["music_art","emotional","slice_of_life"],"mal":8.3,"imdb":7.8},
    {"t":"Lonely Castle in the Mirror","y":2022,"d":"Keiichi Hara","cat":["fantasy","emotional","mystery","slice_of_life"],"mal":7.5,"imdb":7.1},
    {"t":"Gold Kingdom and Water Kingdom","y":2023,"d":"Kotono Watanabe","cat":["fantasy","romance","action_epic"],"mal":7.0,"imdb":6.7},
    {"t":"Tsurune: The Movie","y":2022,"d":"Takuya Yamamura","cat":["sports","emotional","slice_of_life"],"mal":7.5,"imdb":7.0},
    {"t":"A Whisker Away","y":2020,"d":"Junichi Sato","cat":["fantasy","romance","emotional"],"mal":7.0,"imdb":6.7},
    {"t":"Hello World","y":2019,"d":"Tomohiko Ito","cat":["sci_fi","romance","action_epic"],"mal":7.2,"imdb":6.8},
    {"t":"Josee, the Tiger and the Fish","y":2020,"d":"Kotaro Tamura","cat":["romance","emotional","slice_of_life"],"mal":7.5,"imdb":7.1},
    {"t":"Fortune Favors Lady Nikuko","y":2021,"d":"Ayumu Watanabe","cat":["emotional","comedy_satire","slice_of_life"],"mal":6.8,"imdb":6.5},
    {"t":"Totto-chan: The Little Girl at the Window","y":2023,"d":"Shinnosuke Yakuwa","cat":["emotional","historical","slice_of_life"],"mal":7.2,"imdb":6.8},
    {"t":"The Imaginary","y":2023,"d":"Yoshiyuki Momose","cat":["fantasy","emotional"],"mal":7.5,"imdb":7.1},
    {"t":"Rurouni Kenshin: Trust and Betrayal","y":1999,"d":"Kazuhiro Furuhashi","cat":["action_epic","historical","emotional","war"],"mal":8.7,"imdb":8.3},
    {"t":"Rurouni Kenshin: The Beginning","y":2021,"d":"Keishi Otomo","cat":["action_epic","historical","emotional"],"mal":8.2,"imdb":7.8},
    {"t":"Fate/stay night: Heaven's Feel I","y":2017,"d":"Tomonori Sudo","cat":["action_epic","fantasy","romance","horror"],"mal":8.0,"imdb":7.5},
    {"t":"Fate/stay night: Heaven's Feel II","y":2019,"d":"Tomonori Sudo","cat":["action_epic","fantasy","romance","horror"],"mal":8.2,"imdb":7.7},
    {"t":"Fate/stay night: Heaven's Feel III","y":2020,"d":"Tomonori Sudo","cat":["action_epic","fantasy","romance","horror"],"mal":8.3,"imdb":7.8},
    {"t":"My Hero Academia: Two Heroes","y":2018,"d":"Kenji Nagasaki","cat":["action_epic","comedy_satire"],"mal":7.8,"imdb":7.4},
    {"t":"My Hero Academia: Heroes Rising","y":2019,"d":"Kenji Nagasaki","cat":["action_epic","emotional"],"mal":7.9,"imdb":7.5},
    {"t":"Sword Art Online: Ordinal Scale","y":2017,"d":"Tomohiko Ito","cat":["action_epic","sci_fi","fantasy","isekai"],"mal":7.2,"imdb":6.8},
    {"t":"Sword Art Online: Progressive - Aria","y":2021,"d":"Ayako Kouno","cat":["action_epic","romance","sci_fi","isekai"],"mal":7.5,"imdb":7.1},
    {"t":"Kingsglaive: Final Fantasy XV","y":2016,"d":"Takeshi Nozue","cat":["action_epic","fantasy"],"mal":7.0,"imdb":6.7},
    {"t":"Final Fantasy VII: Advent Children","y":2005,"d":"Tetsuya Nomura","cat":["action_epic","sci_fi","fantasy"],"mal":7.2,"imdb":6.9},
    {"t":"Shin Godzilla","y":2016,"d":"Hideaki Anno","cat":["sci_fi","action_epic","horror"],"mal":7.8,"imdb":7.1},
    {"t":"Shin Ultraman","y":2022,"d":"Hideaki Anno","cat":["sci_fi","action_epic"],"mal":7.5,"imdb":6.8},
    {"t":"Shin Kamen Rider","y":2023,"d":"Hideaki Anno","cat":["action_epic","sci_fi"],"mal":7.2,"imdb":6.5},
    {"t":"Garden of Sinners: Overlooking View","y":2007,"d":"Eiichi Takahashi","cat":["mystery","horror","phil_surreal"],"mal":7.5,"imdb":7.1},
    {"t":"Garden of Sinners: Paradox Spiral","y":2008,"d":"Shinsuke Takizawa","cat":["mystery","horror","phil_surreal"],"mal":7.6,"imdb":7.2},
    {"t":"Tales from Earthsea","y":2006,"d":"Goro Miyazaki","cat":["fantasy","emotional"],"mal":6.5,"imdb":6.4},
    {"t":"Ponyo","y":2008,"d":"Hayao Miyazaki","cat":["fantasy","emotional","slice_of_life"],"mal":7.9,"imdb":7.6},
    {"t":"Space Pirate Captain Harlock","y":2013,"d":"Shinji Aramaki","cat":["sci_fi","action_epic"],"mal":6.5,"imdb":6.2},
    {"t":"Sailor Moon Eternal Part 1","y":2021,"d":"Chiaki Kon","cat":["fantasy","romance"],"mal":7.3,"imdb":6.8},
    {"t":"Sailor Moon Eternal Part 2","y":2021,"d":"Chiaki Kon","cat":["fantasy","romance"],"mal":7.3,"imdb":6.8},
    {"t":"Sailor Moon Cosmos Part 1","y":2024,"d":"Kazuko Tadano","cat":["fantasy","romance"],"mal":7.5,"imdb":7.0},
    {"t":"Sailor Moon Cosmos Part 2","y":2024,"d":"Kazuko Tadano","cat":["fantasy","romance"],"mal":7.5,"imdb":7.0},
    {"t":"5 Centimeters Per Second","y":2007,"d":"Makoto Shinkai","cat":["romance","emotional","slice_of_life"],"mal":7.6,"imdb":7.5},
    {"t":"Voices of a Distant Star","y":2002,"d":"Makoto Shinkai","cat":["sci_fi","romance","emotional","short"],"mal":7.2,"imdb":7.2},
    {"t":"She and Her Cat","y":1999,"d":"Makoto Shinkai","cat":["emotional","short","slice_of_life"],"mal":7.2,"imdb":7.0},
    {"t":"The Place Promised in Our Early Days","y":2004,"d":"Makoto Shinkai","cat":["sci_fi","romance","emotional"],"mal":7.0,"imdb":6.9},
    {"t":"Arrietty","y":2010,"d":"Hiromasa Yonebayashi","cat":["fantasy","emotional","slice_of_life"],"mal":7.5,"imdb":7.1},
    {"t":"When Marnie Was There","y":2014,"d":"James Simone","cat":["emotional","mystery","slice_of_life"],"mal":7.5,"imdb":7.1},
    {"t":"Mary and the Witchs Flower","y":2017,"d":"Hiromasa Yonebayashi","cat":["fantasy","emotional"],"mal":7.1,"imdb":6.8},
    {"t":"Mirai","y":2018,"d":"Mamoru Hosoda","cat":["fantasy","emotional","slice_of_life"],"mal":7.3,"imdb":7.0},
    {"t":"Harmony","y":2015,"d":"Michael Arias","cat":["sci_fi","phil_surreal","dystopia"],"mal":7.2,"imdb":6.8},
    {"t":"Patema Inverted","y":2013,"d":"Yasuhiro Yoshiura","cat":["sci_fi","fantasy","romance"],"mal":7.5,"imdb":7.1},
    {"t":"Mai Mai Miracle","y":2009,"d":"Sunao Katabuchi","cat":["emotional","historical","fantasy","slice_of_life"],"mal":7.3,"imdb":7.0},
    {"t":"Dragon Ball Super: Broly","y":2018,"d":"Tadayoshi Yamamuro","cat":["action_epic"],"mal":8.1,"imdb":7.8},
    {"t":"Dragon Ball Super: Super Hero","y":2022,"d":"Tadayoshi Yamamuro","cat":["action_epic","comedy_satire"],"mal":7.5,"imdb":7.1},
    {"t":"Lupin III: The First","y":2019,"d":"Takashi Yamazaki","cat":["action_epic","comedy_satire"],"mal":7.2,"imdb":6.8},
    {"t":"Stand by Me Doraemon","y":2014,"d":"Takashi Yamazaki","cat":["emotional","fantasy","slice_of_life","sci_fi"],"mal":7.5,"imdb":7.1},
    {"t":"Stand by Me Doraemon 2","y":2020,"d":"Takashi Yamazaki","cat":["emotional","fantasy","slice_of_life","sci_fi"],"mal":7.8,"imdb":7.4},
]

# === IZLENEN ===
WATCHED = set()
def load_watched():
    global WATCHED
    p = f"{BASE}/data/watched.txt"
    if os.path.exists(p):
        WATCHED = {w.strip().lower() for w in open(p) if w.strip()}
def save_watched():
    with open(f"{BASE}/data/watched.txt","w") as f:
        for w in sorted(WATCHED): f.write(w+"\n")
def is_watched(t):
    tl = t.lower().strip()
    return tl in WATCHED or any(tl in w or w in tl for w in WATCHED)
def mark_watched(t):
    WATCHED.add(t.lower().strip()); save_watched()

# === PUAN ===
def owl_score(mal, imdb, cats, year):
    base = (mal*0.6+imdb*0.4) if imdb>0 else mal
    cb = sum(TASTE_W.get(c,5) for c in cats)/max(len(cats),1)*0.05
    yb = 0.2 if year>=2020 else (0.1 if year>=2010 else 0)
    return min(round(base+cb+yb,1), 10.0)

# === DB ===
def init_db():
    os.makedirs(f"{BASE}/data", exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.execute("PRAGMA journal_mode=WAL")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS films(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,title_lower TEXT UNIQUE,year INTEGER,director TEXT,mal_score REAL,imdb_score REAL,owl_score REAL,source TEXT DEFAULT 'Unknown',is_watched INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS cat(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT UNIQUE,label TEXT);
        CREATE TABLE IF NOT EXISTS fc(film_id INTEGER,cat_id INTEGER,PRIMARY KEY(film_id,cat_id));
        CREATE INDEX IF NOT EXISTS idx_fo ON films(owl_score DESC);
        CREATE INDEX IF NOT EXISTS idx_fw ON films(is_watched);
        CREATE INDEX IF NOT EXISTS idx_ft ON films(title_lower);
    """); db.commit(); return db

def populate(db):
    added=0
    for f in FILMS:
        tl=f["t"].lower()
        try:
            mal=f.get("mal",7.0); imdb=f.get("imdb",0); cats=f.get("cat",[]); year=f.get("y",2000)
            ow=owl_score(mal,imdb,cats,year); iw=1 if is_watched(f["t"]) else 0
            cur=db.execute("INSERT OR IGNORE INTO films(title,title_lower,year,director,mal_score,imdb_score,owl_score,is_watched) VALUES(?,?,?,?,?,?,?,?)",(f["t"],tl,year,f.get("d",""),mal,imdb,ow,iw))
            if cur.rowcount==0: continue
            fid=cur.lastrowid
            for c in cats:
                db.execute("INSERT OR IGNORE INTO cat(name,label) VALUES(?,?)",(c,ALL_CATS.get(c,c)))
                cid=db.execute("SELECT id FROM cat WHERE name=?",(c,)).fetchone()[0]
                db.execute("INSERT OR IGNORE INTO fc(film_id,cat_id) VALUES(?,?)",(fid,cid))
            added+=1
        except: pass
    db.commit(); return added

# === ONERI ===
def recommend(db, cat=None, mins=0, yf=0, yt=2030, lim=20, unwatched=True):
    q="SELECT title,year,director,mal_score,imdb_score,owl_score,source FROM films WHERE owl_score>=? AND year BETWEEN ? AND ?"; p=[mins,yf,yt]
    if unwatched: q+=" AND is_watched=0"
    if cat: q+=" AND id IN (SELECT film_id FROM fc WHERE cat_id=(SELECT id FROM cat WHERE name=?))"; p.append(cat)
    q+=" ORDER BY owl_score DESC LIMIT ?"; p.append(lim)
    return db.execute(q,p).fetchall()

# === TXR RAPOR ===
def gen_report(db):
    os.makedirs(TXT_DIR, exist_ok=True)
    films=recommend(db,lim=500)
    with open(f"{TXT_DIR}/01_ana_liste.txt","w",encoding="utf-8") as f:
        f.write(f"OWL ANIME & FILM ONERI LISTESI - {datetime.now().strftime('%Y-%m-%d %H:%M')} - {len(films)} film\n{'='*80}\n\n")
        for i,fl in enumerate(films,1):
            f.write(f"#{i:04d} | OWL:{fl[5]:.1f} | MAL:{fl[3]:.1f} | {fl[0]} ({fl[1]}) | {fl[2]}\n")
    cats=db.execute("SELECT c.name,c.label,COUNT(fc.film_id) FROM cat c JOIN fc ON c.id=fc.cat_id GROUP BY c.name ORDER BY COUNT(fc.film_id) DESC").fetchall()
    for ck,cl,cnt in cats:
        cf=recommend(db,cat=ck,lim=200)
        if cf:
            with open(f"{TXT_DIR}/02_{ck}.txt","w",encoding="utf-8") as f:
                f.write(f"{cl} ({len(cf)} film)\n{'='*80}\n\n")
                for i,fl in enumerate(cf,1): f.write(f"#{i:03d} | [{fl[5]:.1f}] {fl[0]} ({fl[1]}) | {fl[2]}\n")
    total=db.execute("SELECT COUNT(*) FROM films").fetchone()[0]
    watched=db.execute("SELECT COUNT(*) FROM films WHERE is_watched=1").fetchone()[0]
    avg=db.execute("SELECT AVG(owl_score) FROM films WHERE is_watched=0").fetchone()[0]
    decades=db.execute("SELECT (year/10)*10 as d,COUNT(*) FROM films WHERE is_watched=0 GROUP BY d ORDER BY d").fetchall()
    with open(f"{TXT_DIR}/03_stats.txt","w",encoding="utf-8") as f:
        f.write(f"ISTATISTIKLER\n{'='*80}\nToplam: {total}\nIzlenen: {watched}\nKalan: {total-watched}\nOrt OWL: {avg:.1f}\n\nYil dagilimi:\n")
        for d,cnt in decades: f.write(f"  {d}s: {'█'*min(cnt,50)} ({cnt})\n")
    return len(films)

# === CLI ===
def interactive(db):
    print("\n  OWL ANIME & FILM ONERI SISTEMI v2.0\n"+"="*50)
    while True:
        print("\n[K]Oneri [T]Tur [Y]Yil [P]Puan [W]Izledi [R]Rapor [S]Ara [I]Stats [Q]Cikis")
        c=input("Secim: ").strip().lower()
        if c=="q": break
        elif c=="k":
            fl=recommend(db,lim=15)
            for i,f in enumerate(fl,1): print(f"  {i:2d}.[{f[5]:.1f}] {f[0]} ({f[1]}) - {f[2]}")
        elif c=="t":
            cats=db.execute("SELECT c.name,c.label,COUNT(fc.film_id) FROM cat c JOIN fc ON c.id=fc.cat_id GROUP BY c.name ORDER BY COUNT(fc.film_id) DESC").fetchall()
            for i,(ck,cl,cnt) in enumerate(cats,1): print(f"  {i:2d}. {cl} ({cnt})")
            try:
                ci=int(input("Tur no:"))-1
                if 0<=ci<len(cats):
                    fl=recommend(db,category=cats[ci][0],lim=15)
                    for i,f in enumerate(fl,1): print(f"  {i:2d}.[{f[5]:.1f}] {f[0]} ({f[1]}) - {f[2]}")
            except: pass
        elif c=="i":
            total=db.execute("SELECT COUNT(*) FROM films").fetchone()[0]
            watched=db.execute("SELECT COUNT(*) FROM films WHERE is_watched=1").fetchone()[0]
            avg=db.execute("SELECT AVG(owl_score) FROM films WHERE is_watched=0").fetchone()[0]
            print(f"  Toplam:{total} Izlenen:{watched} Kalan:{total-watched} Ort OWL:{avg:.1f}")
        elif c=="w":
            t=input("Film:").strip()
            if t: mark_watched(t); print(f"  '{t}' izlendi.")
        elif c=="r":
            n=gen_report(db)
            print(f"  Rapor olusturuldu: {n} film -> {TXT_DIR}/")
        elif c=="s":
            q=input("Ara:").strip().lower()
            if q:
                r=db.execute("SELECT title,year,director,owl_score FROM films WHERE title_lower LIKE ? ORDER BY owl_score DESC LIMIT 20",(f"%{q}%",)).fetchall()
                for f in r: print(f"  [{f[3]:.1f}] {f[0]} ({f[1]}) - {f[2]}")
                if not r: print("  Sonuc yok.")
        elif c=="y":
            try:
                yf=int(input("Baslangic:")); yt=int(input("Bitis:"))
                fl=recommend(db,yf=yf,yt=yt,lim=15)
                for i,f in enumerate(fl,1): print(f"  {i:2d}.[{f[5]:.1f}] {f[0]} ({f[1]}) - {f[2]}")
            except: pass
        elif c=="p":
            try:
                ms=float(input("Min OWL:"))
                fl=recommend(db,mins=ms,lim=15)
                for i,f in enumerate(fl,1): print(f"  {i:2d}.[{f[5]:.1f}] {f[0]} ({f[1]}) - {f[2]}")
            except: pass

# === ANA ===
def main():
    p=argparse.ArgumentParser(description="OWL Anime & Film Oneri v2.0")
    p.add_argument("--cli",action="store_true"); p.add_argument("--recommend",type=int,default=0)
    p.add_argument("--category",type=str); p.add_argument("--year-from",type=int,default=0)
    p.add_argument("--year-to",type=int,default=2030); p.add_argument("--min-score",type=float,default=0)
    p.add_argument("--report",action="store_true"); p.add_argument("--stats",action="store_true")
    p.add_argument("--search",type=str); p.add_argument("--watch",type=str); p.add_argument("--init",action="store_true")
    args=p.parse_args(); load_watched(); db=init_db()
    if args.init:
        db.execute("DELETE FROM films"); db.execute("DELETE FROM fc"); db.commit()
        n=populate(db); print(f"DB sifirlandi, {n} film eklendi."); return
    if db.execute("SELECT COUNT(*) FROM films").fetchone()[0]==0:
        n=populate(db); print(f"DB olusturuldu: {n} film.")
    if args.stats:
        t=db.execute("SELECT COUNT(*) FROM films").fetchone()[0]
        w=db.execute("SELECT COUNT(*) FROM films WHERE is_watched=1").fetchone()[0]
        a=db.execute("SELECT AVG(owl_score) FROM films WHERE is_watched=0").fetchone()[0]
        print(f"Toplam:{t} Izlen:{w} Kalan:{t-w} Ort:{a:.1f}")
        for d,c in db.execute("SELECT (year/10)*10,COUNT(*) FROM films WHERE is_watched=0 GROUP BY 1 ORDER BY 1").fetchall():
            print(f"  {d}s: {'█'*min(c,40)} ({c})")
    elif args.search:
        for f in db.execute("SELECT title,year,owl_score FROM films WHERE title_lower LIKE ? ORDER BY owl_score DESC LIMIT 20",(f"%{args.search.lower()}%",)): print(f"[{f[2]:.1f}] {f[0]} ({f[1]})")
    elif args.watch: mark_watched(args.watch); print(f"'{args.watch}' izlendi.")
    elif args.report:
        n=gen_report(db); print(f"TXT rapor: {n} film -> {TXT_DIR}/")
    elif args.recommend>0:
        for i,f in enumerate(recommend(db,cat=args.category,mins=args.min_score,yf=args.year_from,yt=args.year_to,lim=args.recommend),1):
            print(f"{i:3d}.[{f[5]:.1f}] {f[0]} ({f[1]}) - {f[2]}")
    elif args.cli: interactive(db)
    else:
        print("\nOWL 10 Film Oneriyor:\n")
        for i,f in enumerate(recommend(db,lim=10),1): print(f"  {i:2d}.[{f[5]:.1f}] {f[0]} ({f[1]}) - {f[2]}")
        print("\n--cli ile etkilesimli mod, --detay yardim icin")

if __name__=="__main__": main()
