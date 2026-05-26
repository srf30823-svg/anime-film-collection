"""Hermes APK - Ana Ekran (Home)"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.lang import Builder

from ui.theme import COLORS, DIMS, LAIN_STATUS, LAIN_MESSAGES

Builder.load_string('''
<HomeScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: root.DIMS['padding_lg']
        spacing: root.DIMS['padding_md']
        
        # Ust status bar
        BoxLayout:
            size_hint_y: None
            height: 60
            spacing: 8
            
            Label:
                text: '◇  H E R M E S'
                font_size: root.DIMS['font_lg']
                color: root.COLORS['primary_light']
                size_hint_x: 0.7
                halign: 'left'
                text_size: self.size
            
            # Status dot
            Widget:
                size_hint: None, None
                size: 12, 12
                pos_hint: {'center_y': 0.5}
                canvas:
                    Color:
                        rgba: root.COLORS['success'] if root.is_online else root.COLORS['danger']
                    Ellipse:
                        pos: self.pos
                        size: self.size
            
            Label:
                text: root.gateway_status
                font_size: root.DIMS['font_sm']
                color: root.COLORS['text_dim']
                size_hint_x: 0.3
        
        # Ayirici
        Widget:
            size_hint_y: None
            height: 1
            canvas:
                Color:
                    rgba: root.COLORS['border']
                Rectangle:
                    pos: self.pos
                    size: self.size
        
        # Context gosterge
        BoxLayout:
            size_hint_y: None
            height: 40
            spacing: 8
            
            Label:
                text: 'Context:'
                font_size: root.DIMS['font_sm']
                color: root.COLORS['text_dim']
                size_hint_x: 0.3
                text_size: self.size
            
            ProgressBar:
                value: root.context_pct
                max: 100
                size_hint_x: 0.5
            
            Label:
                text: '{}%'.format(int(root.context_pct))
                font_size: root.DIMS['font_sm']
                color: root.COLORS['text']
                size_hint_x: 0.2
                text_size: self.size
        
        # Hizli erisim kartlari
        GridLayout:
            cols: 2
            spacing: root.DIMS['padding_md']
            size_hint_y: None
            height: 200
            
            # Anime karti
            Button:
                text: '⌬\\nAnime'
                background_color: 0,0,0,0
                background_normal: ''
                color: root.COLORS['text']
                font_size: root.DIMS['font_md']
                on_release: root.manager.current = 'ani'
                canvas.before:
                    Color:
                        rgba: root.COLORS['bg_card']
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [root.DIMS['radius_md']]
                    Color:
                        rgba: root.COLORS['primary']
                    Line:
                        rounded_rectangle: self.x, self.y, self.width, self.height, root.DIMS['radius_md']
                        width: 1.5
            
            # Git karti
            Button:
                text: '◈\\nGit'
                background_color: 0,0,0,0
                background_normal: ''
                color: root.COLORS['text']
                font_size: root.DIMS['font_md']
                on_release: root.manager.current = 'git'
                canvas.before:
                    Color:
                        rgba: root.COLORS['bg_card']
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [root.DIMS['radius_md']]
                    Color:
                        rgba: root.COLORS['secondary']
                    Line:
                        rounded_rectangle: self.x, self.y, self.width, self.height, root.DIMS['radius_md']
                        width: 1.5
            
            # Sistem karti
            Button:
                text: '⬡\\nSystem'
                background_color: 0,0,0,0
                background_normal: ''
                color: root.COLORS['text']
                font_size: root.DIMS['font_md']
                on_release: root.manager.current = 'sys'
                canvas.before:
                    Color:
                        rgba: root.COLORS['bg_card']
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [root.DIMS['radius_md']]
                    Color:
                        rgba: root.COLORS['accent']
                    Line:
                        rounded_rectangle: self.x, self.y, self.width, self.height, root.DIMS['radius_md']
                        width: 1.5
            
            # LLM karti
            Button:
                text: '◇\\nLLM'
                background_color: 0,0,0,0
                background_normal: ''
                color: root.COLORS['text']
                font_size: root.DIMS['font_md']
                on_release: root.manager.current = 'llm'
                canvas.before:
                    Color:
                        rgba: root.COLORS['bg_card']
                    RoundedRectangle:
                        pos: self.pos
                    radius: [root.DIMS['radius_md']]
                    Color:
                        rgba: root.COLORS['primary_light']
                    Line:
                        rounded_rectangle: self.x, self.y, self.width, self.height, root.DIMS['radius_md']
                        width: 1.5
        
        # Alt kisim - Son aktiviteler
        Label:
            text: 'Son Aktiviteler'
            font_size: root.DIMS['font_sm']
            color: root.COLORS['text_dim']
            size_hint_y: None
            height: 30
            halign: 'left'
            text_size: self.size
        
        ScrollView:
            do_scroll_x: False
            BoxLayout:
                id: activity_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 4
        
        Widget:
            size_hint_y: 1
''')

class HomeScreen(Screen):
    COLORS = COLORS
    DIMS = DIMS
    gateway_status = StringProperty("Wired")
    context_pct = NumericProperty(15)
    is_online = BooleanProperty(True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._activities = []
        Clock.schedule_once(self._init_activities, 0)
        Clock.schedule_interval(self._simulate_context, 2)
    
    def _init_activities(self, dt):
        acts = [
            "✓ Anime oneri motoru hazir",
            "✓ Script-LLM motoru aktif",
            "✓ Git sync tamamlandi",
            "✓ Sistem taramasi yapildi",
        ]
        for a in acts:
            self._add_activity(a)
    
    def _add_activity(self, text):
        from kivy.uix.label import Label
        lbl = Label(
            text=f"  {text}",
            font_size=DIMS['font_sm'],
            color=COLORS['text_dim'],
            size_hint_y=None,
            height=28,
            halign='left',
            text_size=(300, None)
        )
        self.ids.activity_list.add_widget(lbl)
    
    def _simulate_context(self, dt):
        self.context_pct = min(self.context_pct + 0.5, 95)
