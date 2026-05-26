"""Hermes APK - Anime/Film Oneri Ekrani"""
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.clock import Clock
from ui.theme import COLORS, DIMS

Builder.load_string('''
<AniScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: root.DIMS['padding_md']
        spacing: root.DIMS['padding_sm']
        
        # Arama
        BoxLayout:
            size_hint_y: None
            height: root.DIMS['input_height']
            spacing: 8
            
            TextInput:
                id: search_input
                hint_text: 'Anime/film ara...'
                background_color: root.COLORS['bg_input']
                foreground_color: root.COLORS['text']
                hint_text_color: root.COLORS['text_muted']
                cursor_color: root.COLORS['primary_light']
                font_size: root.DIMS['font_md']
                padding: [12, 12]
                multiline: False
                on_text_validate: root.do_search(self.text)
                canvas.before:
                    Color:
                        rgba: root.COLORS['border']
                    Line:
                        rounded_rectangle: self.x, self.y, self.width, self.height, root.DIMS['radius_sm']
                        width: 1
            
            Button:
                text: '⌕'
                size_hint_x: None
                width: root.DIMS['input_height']
                background_color: 0,0,0,0
                color: root.COLORS['primary_light']
                font_size: root.DIMS['font_lg']
                on_release: root.do_search(search_input.text)
                canvas.before:
                    Color:
                        rgba: root.COLORS['primary']
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [root.DIMS['radius_sm']]
        
        # Filtre chip'leri
        ScrollView:
            size_hint_y: None
            height: 40
            do_scroll_y: False
            BoxLayout:
                id: filter_chips
                size_hint_x: None
                width: self.minimum_width
                spacing: 8
                padding: [0, 4]
        
        # Sonuclar
        Label:
            text: root.status_text
            font_size: root.DIMS['font_sm']
            color: root.COLORS['text_dim']
            size_hint_y: None
            height: 30
            text_size: self.size
            halign: 'left'
        
        ScrollView:
            do_scroll_x: False
            BoxLayout:
                id: results_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: root.DIMS['padding_sm']
        
        # Rastgele oner FAB
        Button:
            text: '⟐'
            size_hint: None, None
            size: root.DIMS['fab_size'], root.DIMS['fab_size']
            pos_hint: {'right': 0.95, 'y': 0.02}
            background_color: 0,0,0,0
            color: root.COLORS['text']
            font_size: root.DIMS['font_xl']
            on_release: root.random_recommend()
            canvas.before:
                Color:
                    rgba: root.COLORS['primary']
                Ellipse:
                    pos: self.pos
                    size: self.size
                Color:
                    rgba: root.COLORS['primary_light']
                Line:
                    ellipse: self.x, self.y, self.width, self.height
                    width: 1.5
''')

class AniScreen(Screen):
    COLORS = COLORS
    DIMS = DIMS
    status_text = "Hazir. Arama yap veya rastgele oner al."
    
    _filters = ["Hepsi", "Felsefi", "Aksiyon", "Duygusal", "Komedi", "BilimKurgu", "Fantastik", "Psikolojik", "Tarihi", "Spor"]
    _demo_films = [
        ("Spirited Away", 2001, "Miyazaki", 8.8, "Fantastik"),
        ("A Silent Voice", 2016, "Yamada", 8.9, "Duygusal"),
        ("Perfect Blue", 1997, "Kon", 8.5, "Psikolojik"),
        ("Ghost in the Shell", 1995, "Oshii", 8.3, "BilimKurgu"),
        ("Princess Mononoke", 1997, "Miyazaki", 8.7, "Fantastik"),
        ("Akira", 1988, "Otomo", 8.2, "BilimKurgu"),
        ("Wolf Children", 2012, "Hosoda", 8.6, "Duygusal"),
        ("Mind Game", 2004, "Yuasa", 7.9, "Felsefi"),
        ("Redline", 2009, "Koike", 8.2, "Aksiyon"),
        ("The Tatami Galaxy", 2010, "Yuasa", 8.5, "Felsefi"),
        ("Paprika", 2006, "Kon", 8.0, "Psikolojik"),
        ("Grave of the Fireflies", 1988, "Takahata", 8.5, "Duygusal"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._init_filters, 0)
        Clock.schedule_once(self._show_all, 0)
    
    def _init_filters(self, dt):
        from kivy.uix.button import Button
        for f in self._filters:
            btn = Button(
                text=f,
                size_hint=(None, None),
                size=(80, 32),
                background_color=(0,0,0,0),
                color=COLORS['text_dim'],
                font_size=DIMS['font_xs'],
                on_release=lambda x, flt=f: self.do_filter(flt)
            )
            btn.canvas.before.add(None)  # placeholder
            self.ids.filter_chips.add_widget(btn)
    
    def _show_all(self, dt):
        self._render_films(self._demo_films)
        self.status_text = f"{len(self._demo_films)} film listelendi"
    
    def _render_films(self, films):
        self.ids.results_list.clear_widgets()
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        for title, year, director, score, genre in films:
            card = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=72,
                padding=DIMS['padding_sm'],
                spacing=2
            )
            # Ust satir: film adi + puan
            top = BoxLayout(size_hint_y=0.6)
            top.add_widget(Label(
                text=f"  {title}",
                font_size=DIMS['font_sm'],
                color=COLORS['text'],
                halign='left',
                text_size=(250, None),
                shorten=True
            ))
            top.add_widget(Label(
                text=f"[{score}]",
                font_size=DIMS['font_sm'],
                color=COLORS['primary_light'],
                size_hint_x=0.3
            ))
            card.add_widget(top)
            # Alt satir: yil + yonetmen + tur
            bottom = BoxLayout(size_hint_y=0.4)
            bottom.add_widget(Label(
                text=f"  {year} • {director}",
                font_size=DIMS['font_xs'],
                color=COLORS['text_dim'],
                halign='left',
                text_size=(200, None)
            ))
            # Tur badge
            badge = Label(
                text=genre,
                font_size=DIMS['font_xs']-1,
                color=COLORS['secondary'],
                size_hint_x=0.3,
                halign='right',
                text_size=(80, None)
            )
            bottom.add_widget(badge)
            card.add_widget(bottom)
            
            self.ids.results_list.add_widget(card)
    
    def do_search(self, query):
        if not query.strip():
            self._show_all(0)
            return
        q = query.lower()
        results = [f for f in self._demo_films if q in f[0].lower() or q in f[4].lower()]
        self._render_films(results)
        self.status_text = f"'{query}' icin {len(results)} sonuc"
    
    def do_filter(self, flt):
        if flt == "Hepsi":
            self._show_all(0)
            return
        genre_map = {
            "Felsefi": "Felsefi", "Aksiyon": "Aksiyon", "Duygusal": "Duygusal",
            "Komedi": "Komedi", "BilimKurgu": "BilimKurgu", "Fantastik": "Fantastik",
            "Psikolojik": "Psikolojik", "Tarihi": "Tarihi", "Spor": "Spor"
        }
        results = [f for f in self._demo_films if flt in f[4]]
        self._render_films(results)
        self.status_text = f"Filtre: {flt} ({len(results)} film)"
    
    def random_recommend(self):
        import random
        pick = random.sample(self._demo_films, min(3, len(self._demo_films)))
        self._render_films(pick)
        self.status_text = "🎲 Rastgele 3 oneri"
