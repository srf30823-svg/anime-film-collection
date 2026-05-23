#!/usr/bin/env python3
"""
OWL - Kapsamlı Anime Film + Web Novel Analiz Sistemi
Veritabanı modülü
"""

# Kullanıcının izlediği anime filmleri
WATCHED = set([
    "dragon ball", "dragon ball z", "dragon ball super", "dragon ball super: broly",
    "dragon ball super: super hero", "dragon ball z: battle of gods",
    "dragon ball z: resurrection f", "dragon ball z: fusion reborn",
    "dragon ball z: wrath of the dragon", "dragon ball: the path to power",
    "dragon ball: sleeping princess in devil's castle", "dragon ball: mystical adventure",
    "dragon ball: curse of the blood rubies", "dragon ball: princess snake",
    "serial experiments lain", "re:zero", "gintama", "gintama: the final",
    "gintama: the very final", "mob psycho 100", "mob psycho 100: the spirits",
    "dororo", "solo leveling", "mushishi", "mushishi: the next chapter",
    "demon slayer", "demon slayer: mugen train", "demon slayer: infinity train",
    "haikyuu", "haikyuu!!", "haikyuu!! the dumpster battle",
    "haikyuu!! winners and losers", "haikyuu!! the end and the beginning",
    "haikyuu!! talent and sense", "haikyuu!! concept no tatakai",
    "your name", "weathering with you", "suzume", "5 centimeters per second",
    "the garden of words", "children who chase lost voices",
    "spirited away", "princess mononoke", "my neighbor totoro",
    "howl's moving castle", "castle in the sky", "kiki's delivery service",
    "nausicaa of the valley of the wind", "porco rosso", "ponyo",
    "the wind rises", "a silent voice", "wolf children",
    "the girl who leapt through time", "summer wars", "belle", "mirai",
    "perfect blue", "millennium actress", "tokyo godfathers", "paprika",
    "akira", "ghost in the shell", "ghost in the shell 2: innocence",
    "the end of evangelion", "evangelion: 3.0+1.0 thrice upon a time",
    "redline", "promare", "mind game", "tekkonkinkreet",
    "in this corner of the world", "maquia: when the promised flower blooms",
    "jujutsu kaisen 0", "the first slam dunk", "sword of the stranger",
    "violet evergarden: the movie", "liz and the blue bird",
    "kizumonogatari part 1: tekketsu", "kizumonogatari part 2: nekketsu",
    "kizumonogatari part 3: reiketsu",
    "puella magi madoka magica: rebellion",
    "ride your wave", "the night is short, walk on girl",
    "inu-oh", "children of the sea",
    "fate/stay night: heaven's feel i. presage flower",
    "fate/stay night: heaven's feel ii. lost butterfly",
    "fate/stay night: heaven's feel iii. spring song",
    "one piece: stampede", "one piece film: red",
    "spy x family code: white",
    "chainsaw man: reze arc",
    "the boy and the heron",
    "mononoke the movie: phantom in the rain",
    "sailor moon cosmos", "sailor moon eternal",
    "digimon adventure: last evolution kizuna",
    "my hero academia: two heroes", "my hero academia: heroes rising",
    "my hero academia: world heroes mission",
    "detective conan: the fist of blue sapphire",
    "detective conan: zero the enforcer",
    "lupin iii: the first",
    "grave of the fireflies", "only yesterday", "pom poko",
    "the tale of the princess kaguya", "my neighbors the yamadas",
    "whisper of the heart", "the cat returns", "ocean waves",
    "arrietty", "when marnie was there", "mary and the witch's flower",
    "tales from earthsea", "from up on poppy hill",
    "the colors within", "tamako love story", "k-on! the movie",
    "patlabor: the movie", "patlabor 2: the movie",
    "jin-roh: the wolf brigade", "blood: the last vampire",
    "ninja scroll", "vampire hunter d: bloodlust",
    "x/1999", "cardcaptor sakura: the movie",
    "escaflowne: the movie",
    "berserk: golden age arc", "mobile suit gundam: char's counterattack",
    "mobile suit gundam: hathaway",
    "rurouni kenshin: trust & betrayal",
    "gurren lagann: childhood's end",
    "royal space force: the wings of honneamise",
    "angel's egg", "urusei yatsura 2: beautiful dreamer",
    "the sky crawlers", "avalon", "talking head",
    "steamboy", "roujin z", "memories", "metropolis",
    "gunbuster", "diebuster", "gunbuster vs. diebuster",
    "knights of sidonia", "blame!", "levius",
    "modest heroes", "tomorrow's joe",
    "sword art online: ordinal scale",
    "sword art online: progressive - aria of a starless night",
    "garden of sinners: overlooking view",
    "garden of sinners: remaining sense of pain",
    "garden of sinners: the hollow shrine",
    "garden of sinners: paradox spiral",
    "shin godzilla", "shin ultaman", "shin kamen rider",
    "attack on titan: chronicle",
    "ranking of kings: the treasure chest of courage",
    "zombie land saga: revenge",
    "colorful", "summer days with coo", "miss hokusai",
    "anthem of the heart", "her blue sky",
    "free! take your marks",
    "little witch academia", "kill la kill: if",
    "cowboy bebop: the movie",
    "fullmetal alchemist: the sacred star of milos",
    "psycho-pass: the movie",
    "009 re:cyborg",
    "kabaneri of the iron fortress: the battle of unato",
    "saga of tanya the evil: the movie",
    "attack on titan: the roar of awakening",
    "clannad: the movie",
    "the disappearance of haruhi suzumiya",
    "sound! euphonium: the movie",
    "the wonderful world of puss 'n boots",
    "galaxy express 999",
    "adieu galaxy express 999",
    "arcadia of my youth",
    "saint seiya: legend of sanctuary",
    "dragon ball: dead zone",
    "dragon ball z: the world's strongest",
    "dragon ball z: the tree of might",
    "dragon ball z: lord slug",
    "dragon ball z: cooler's revenge",
    "dragon ball z: return of cooler",
    "dragon ball z: super android 13",
    "dragon ball z: bojack unbound",
    "dragon ball z: broly - the legendary super saiyan",
    "one piece: the movie",
    "one piece: clockwork island adventure",
    "one piece: chopper's kingdom on the island of strange animals",
    "one piece: dead end adventure",
    "one piece: the cursed holy sword",
    "one piece: baron omatsuri and the secret island",
    "one piece: the giant mechanical soldier of karakuri castle",
    "one piece: episode of alabasta",
    "one piece: episode of chopper plus",
    "one piece film: strong world",
    "one piece: 3d2y",
    "one piece film: gold",
    "sailor moon r: the movie",
    "sailor moon s: the movie",
    "sailor moon supers: the movie",
    "digimon adventure: our war game!",
    "digimon adventure 02: revenge of diaboromon",
    "digimon tamers: battle of adventurers",
    "digimon tamers: runaway locomon",
    "digimon frontier: island of lost digimon",
    "digimon adventure tri.",
])

def is_watched(title):
    t = title.lower().strip()
    for w in WATCHED:
        if t in w or w in t:
            return True
    return False

# Zevk profili
TASTE = {
    "action_epic": 9, "philosophical_surreal": 10, "comedy_satirical": 8,
    "emotional_slice": 8, "sci_fi": 7, "fantasy_adventure": 8,
    "romance_drama": 5, "horror_thriller": 6, "sports": 7,
    "historical": 6, "mystery": 7, "psychological": 9,
    "cyberpunk": 9, "mecha": 6, "music_art": 7, "short_film": 7,
}

CAT_NAMES = {
    "philosophical_surreal": "Felsefi & Surreal",
    "action_epic": "Aksiyon & Muthis",
    "psychological": "Psikolojik & Zihin Oyunu",
    "comedy_satirical": "Komedi & Satirik",
    "emotional_slice": "Duygusal & Incelikli",
    "fantasy_adventure": "Fantastik & Macera",
    "sci_fi": "Bilim Kurgu",
    "cyberpunk": "Cyberpunk & Tekno-Gerilim",
    "mystery": "Gizem & Dedektif",
    "horror_thriller": "Korku & Gerilim",
    "romance_drama": "Romantik & Drama",
    "sports": "Spor",
    "historical": "Tarihi & Savas",
    "music_art": "Muzik & Sanat",
    "mecha": "Mekka & Robot",
    "short_film": "Kisa Film",
}

def taste_score(cats):
    if not cats:
        return 5.0
    return round(sum(TASTE.get(c, 5) for c in cats) / len(cats), 1)

def owl_score(mal, imdb, cats):
    base = (mal * 0.6 + imdb * 0.4) if imdb > 0 else mal
    bonus = taste_score(cats) * 0.1
    return min(round(base + bonus, 1), 10.0)

def get_source(title):
    known = {
        "akira": "Manga", "ghost in the shell": "Manga", "perfect blue": "Novel",
        "millennium actress": "Original", "tokyo godfathers": "Original",
        "paprika": "Novel", "spirited away": "Original", "princess mononoke": "Original",
        "my neighbor totoro": "Original", "howl's moving castle": "Novel",
        "castle in the sky": "Original", "kiki's delivery service": "Novel",
        "nausicaa of the valley of the wind": "Manga", "porco rosso": "Original",
        "ponyo": "Original", "the wind rises": "Original", "grave of the fireflies": "Novel",
        "only yesterday": "Manga", "pom poko": "Original",
        "the tale of the princess kaguya": "Folklore", "whisper of the heart": "Manga",
        "the cat returns": "Original", "a silent voice": "Manga",
        "wolf children": "Original", "the girl who leapt through time": "Novel",
        "summer wars": "Original", "belle": "Original", "mirai": "Original",
        "redline": "Original", "promare": "Original", "mind game": "Manga",
        "tekkonkinkreet": "Manga", "in this corner of the world": "Manga",
        "maquia: when the promised flower blooms": "Original",
        "jujutsu kaisen 0": "Manga", "the first slam dunk": "Manga",
        "sword of the stranger": "Original", "violet evergarden": "Light Novel",
        "liz and the blue bird": "Light Novel", "kizumonogatari": "Light Novel",
        "madoka magica: rebellion": "Original", "ride your wave": "Original",
        "the night is short, walk on girl": "Novel", "inu-oh": "Novel",
        "children of the sea": "Manga", "fate/stay night: heaven's feel": "Visual Novel",
        "one piece: stampede": "Manga", "one piece film: red": "Manga",
        "spy x family code: white": "Manga", "chainsaw man: reze arc": "Manga",
        "the boy and the heron": "Novel", "mononoke the movie": "TV Series",
        "sailor moon cosmos": "Manga", "sailor moon eternal": "Manga",
        "digimon adventure: last evolution kizuna": "Original",
        "my hero academia: two heroes": "Manga", "my hero academia: heroes rising": "Manga",
        "my hero academia: world heroes mission": "Manga",
        "detective conan: the fist of blue sapphire": "Manga",
        "detective conan: zero the enforcer": "Manga", "lupin iii: the first": "Manga",
        "arrietty": "Novel", "when marnie was there": "Novel",
        "mary and the witch's flower": "Novel", "tales from earthsea": "Novel",
        "from up on poppy hill": "Manga", "the colors within": "Original",
        "tamako love story": "Original", "k-on! the movie": "Manga",
        "patlabor: the movie": "Original", "patlabor 2: the movie": "Original",
        "jin-roh: the wolf brigade": "Original", "blood: the last vampire": "Original",
        "ninja scroll": "Original", "vampire hunter d: bloodlust": "Novel",
        "x/1999": "Manga", "cardcaptor sakura: the movie": "Manga",
        "escaflowne: the movie": "TV Series",
        "berserk: golden age arc": "Manga",
        "mobile suit gundam: char's counterattack": "TV Series",
        "mobile suit gundam: hathaway": "Novel",
        "rurouni kenshin: trust & betrayal": "Manga",
        "gurren lagann: childhood's end": "TV Series",
        "royal space force: the wings of honneamise": "Original",
        "angel's egg": "Original", "urusei yatsura 2: beautiful dreamer": "Manga",
        "the sky crawlers": "Novel", "avalon": "Original",
        "steamboy": "Original", "roujin z": "Original", "memories": "Manga",
        "metropolis": "Manga", "gunbuster": "Original", "diebuster": "Original",
        "knights of sidonia": "Manga", "blame!": "Manga",
        "modest heroes": "Original", "tomorrow's joe": "Manga",
        "sword art online: ordinal scale": "Light Novel",
        "sword art online: progressive - aria of a starless night": "Light Novel",
        "garden of sinners: overlooking view": "Novel",
        "garden of sinners: remaining sense of pain": "Novel",
        "garden of sinners: the hollow shrine": "Novel",
        "garden of sinners: paradox spiral": "Novel",
        "shin godzilla": "Original", "shin ultaman": "Original", "shin kamen rider": "Original",
        "attack on titan: chronicle": "Manga",
        "ranking of kings: the treasure chest of courage": "Manga",
        "zombie land saga: revenge": "Original",
        "colorful": "Novel", "summer days with coo": "Original", "miss hokusai": "Manga",
        "anthem of the heart": "Original", "her blue sky": "Original",
        "free! take your marks": "TV Series",
        "little witch academia": "Original", "kill la kill: if": "TV Series",
        "cowboy bebop: the movie": "TV Series",
        "fullmetal alchemist: the sacred star of milos": "Manga",
        "psycho-pass: the movie": "TV Series",
        "009 re:cyborg": "Manga",
        "kabaneri of the iron fortress: the battle of unato": "TV Series",
        "saga of tanya the evil: the movie": "Light Novel",
        "attack on titan: the roar of awakening": "Manga",
        "clannad: the movie": "Visual Novel",
        "the disappearance of haruhi suzumiya": "Light Novel",
        "sound! euphonium: the movie": "Light Novel",
        "your name": "Original", "weathering with you": "Original", "suzume": "Original",
        "5 centimeters per second": "Original", "the garden of words": "Original",
        "children who chase lost voices": "Original",
        "the place promised in our early days": "Original",
        "voices of a distant star": "Original", "she and her cat": "Original",
        "the tatami galaxy": "Novel", "the end of evangelion": "TV Series",
        "evangelion: 1.0 you are (not) alone": "TV Series",
        "evangelion: 2.0 you can (not) advance": "TV Series",
        "evangelion: 3.0 you can (not) redo": "TV Series",
        "evangelion: 3.0+1.0 thrice upon a time": "TV Series",
    }
    for key, source in known.items():
        if key in title.lower():
            return source
    return "Manga/Light Novel/Original"

def has_wn(title):
    wns = [
        "mushoku tensei", "re:zero", "overlord", "that time i got reincarnated as a slime",
        "the rising of the shield hero", "no game no life", "sword art online",
        "log horizon", "konosuba", "grimgar", "ascendance of a bookworm",
        "solo leveling", "omniscient reader", "second life ranker", "tomb raider king",
        "the beginning after the end", "lord of the mysteries", "shadow slave",
        "eleceed", "nano machine", "return of the disaster-class hero",
        "sss-class suicide hunter", "the greatest estate developer",
        "doctor's rebirth", "heavenly demon cultivation simulation",
        "regression instinct", "infinite mage", "the s-classes that i raised",
        "the novels extra", "trash of the count's family",
        "the world after the fall", "kill the hero",
    ]
    for w in wns:
        if w in title.lower():
            return True
    return False

def why_selected(cats, year):
    r = []
    if "philosophical_surreal" in cats:
        r.append("Felsefi derinlik ve surreal anlatim (Lain tarzi)")
    if "psychological" in cats:
        r.append("Psikolojik gerilim ve zihin oyunlari")
    if "cyberpunk" in cats:
        r.append("Cyberpunk estetigi ve teknoloji felsefesi")
    if "action_epic" in cats:
        r.append("Epik aksiyon ve muthis sahneler")
    if "emotional_slice" in cats:
        r.append("Duygusal derinlik ve insani hikaye")
    if "fantasy_adventure" in cats:
        r.append("Yaratici fantastik dunya")
    if "comedy_satirical" in cats:
        r.append("Zekice komedi ve satirik anlatim")
    if "sci_fi" in cats:
        r.append("Bilim kurgu vizyonu")
    if "mystery" in cats:
        r.append("Gizem ve gerilim kurgusu")
    if "music_art" in cats:
        r.append("Muzik/sanat temali yaratici konsept")
    if "historical" in cats:
        r.append("Tarihi derinlik ve otantik atmosfer")
    if "horror_thriller" in cats:
        r.append("Karanlik atmosfer ve gerilim")
    if "sports" in cats:
        r.append("Spor temali motivasyon ve heyecan")
    if "mecha" in cats:
        r.append("Mekka tasarimi ve aksiyon")
    if "short_film" in cats:
        r.append("Kisa ve etkili anlatim")
    if year >= 2020:
        r.append("Yeni cikan, guncel animasyon teknolojisi")
    elif year < 1990:
        r.append("Klasik, tarihi oneme sahip eser")
    if not r:
        r.append("Genel kalite ve izleyici begeni orani")
    return "; ".join(r[:3])

def critic_review(mal):
    if mal >= 8.5:
        return "Basyapit kabul edilir. Animasyon, kurgu ve karakter derinligi mukemmel."
    elif mal >= 8.0:
        return "Cok yuksek kaliteli. Hem gorsel hem anlatimsal acidan ust duzey."
    elif mal >= 7.5:
        return "Yuksek kalite. Turunun en iyi orneklerinden."
    elif mal >= 7.0:
        return "Iyi yapim. Zevk profiline uygun, keyifli izleme."
    elif mal >= 6.5:
        return "Ortalamanin uzerinde. Bazi guclu yonleri var."
    else:
        return "Degerlendirme karmasik. Belirli bir izleyici kitlesine hitap edebilir."

def anim_quality(year):
    if year >= 2020:
        return "Cok Yuksek (Modern dijital animasyon)"
    elif year >= 2010:
        return "Yuksek (Dijital animasyon)"
    elif year >= 2000:
        return "Iyi (Gecis donemi, dijital+geleneksel)"
    elif year >= 1990:
        return "Iyi (Geleneksel animasyon, el cizimi)"
    else:
        return "Tarihi deger (Erken donem animasyon)"

def popularity(mal):
    if mal >= 8.5:
        return "Cok Populer (Top 100)"
    elif mal >= 8.0:
        return "Populer (Top 500)"
    elif mal >= 7.5:
        return "Iyi Bilinen (Top 1000)"
    elif mal >= 7.0:
        return "Nispeten Bilinen (Top 5000)"
    else:
        return "Az Bilinen (Gizemli Mucevher)"

def taste_index(cats):
    if "philosophical_surreal" in cats or "psychological" in cats:
        return "Lain, Perfect Blue, Evangelion severler icin"
    elif "action_epic" in cats:
        return "Dragon Ball, Demon Slayer, Solo Leveling severler icin"
    elif "emotional_slice" in cats:
        return "Mushishi, Dororo, Violet Evergarden severler icin"
    elif "comedy_satirical" in cats:
        return "Gintama, Konosuba severler icin"
    elif "cyberpunk" in cats or "sci_fi" in cats:
        return "Akira, Ghost in the Shell severler icin"
    elif "fantasy_adventure" in cats:
        return "Studio Ghibli, Dororo severler icin"
    else:
        return "Genel anime severler icin"

def char_depth(cats):
    if "psychological" in cats or "philosophical_surreal" in cats:
        return "Cok Derin (Psikolojik profil, ic catisma)"
    elif "emotional_slice" in cats:
        return "Derin (Duygusal gelisim, iliskiler)"
    elif "action_epic" in cats:
        return "Iyi (Guc gelisim, motivasyon)"
    elif "comedy_satirical" in cats:
        return "Iyi (Karakter tabanli mizah)"
    else:
        return "Orta (Tur geregi yeterli)"

def story_quality(cats):
    if "philosophical_surreal" in cats:
        return "Cok Yuksek (Katmanli anlatim, sembolizm)"
    elif "psychological" in cats:
        return "Yuksek (Surukleyici, sürprizler)"
    elif "mystery" in cats:
        return "Yuksek (Gizem, ipuclari, cozum)"
    elif "action_epic" in cats:
        return "Iyi (Tempo, gerilim, doruk noktasi)"
    elif "emotional_slice" in cats:
        return "Yuksek (Doyurucu, dokunakli)"
    else:
        return "Iyi (Tur standartlarini karsiliyor)"
