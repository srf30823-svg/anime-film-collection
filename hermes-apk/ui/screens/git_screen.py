"""Hermes APK - Git Ekranı"""
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.clock import Clock
from ui.theme import COLORS, DIMS

Builder.load_string('''
<GitScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: root.DIMS['padding_md']
        spacing: root.DIMS['padding_sm']
        
        # Ust status
        BoxLayout:
            size_hint_y: None
            height: 50
            spacing: 8
            
            Label:
                text: '◈ Git Yonetimi'
                font_size: root.DIMS['font_lg']
                color: root.COLORS['secondary']
                halign: 'left'
                text_size: self.size
            
            Label:
                text: root.git_status
                font_size: root.DIMS['font_sm']
                color: root.COLORS['text_dim']
                size_hint_x: 0.4
        
        Widget:
            size_hint_y: None
            height: 1
            canvas:
                Color:
                    rgba: root.COLORS['border']
                Rectangle:
                    pos: self.pos
                    size: self.size
        
        # Repo listesi
        ScrollView:
            do_scroll_x: False
            BoxLayout:
                id: repo_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: root.DIMS['padding_sm']
        
        # Commit mesaji
        BoxLayout:
            size_hint_y: None
            height: root.DIMS['input_height']
            spacing: 8
            
            TextInput:
                id: commit_msg
                hint_text: 'Commit mesaji...'
                background_color: root.COLORS['bg_input']
                foreground_color: root.COLORS['text']
                hint_text_color: root.COLORS['text_muted']
                cursor_color: root.COLORS['secondary']
                font_size: root.DIMS['font_sm']
                padding: [12, 12]
                multiline: False
            
            Button:
                text: 'Push'
                size_hint_x: None
                width: 80
                background_color: 0,0,0,0
                color: root.COLORS['text']
                font_size: root.DIMS['font_sm']
                on_release: root.do_push(commit_msg.text)
                canvas.before:
                    Color:
                        rgba: root.COLORS['secondary']
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [root.DIMS['radius_sm']]
''')

class GitScreen(Screen):
    COLORS = COLORS
    DIMS = DIMS
    git_status = "Clean"
    
    _repos = [
        ("anime-film-collection", "Clean", "2 commit ahead"),
        ("hermes-apk", "Modified", "3 files changed"),
        ("phi4-tr", "Clean", "Up to date"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._init_repos, 0)
    
    def _init_repos(self, dt):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        for name, status, detail in self._repos:
            card = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=60,
                padding=DIMS['padding_sm'],
                spacing=8
            )
            # Sol: repo adi + detay
            left = BoxLayout(orientation='vertical', size_hint_x=0.7)
            left.add_widget(Label(
                text=f"  📁 {name}",
                font_size=DIMS['font_sm'],
                color=COLORS['text'],
                halign='left',
                text_size=(200, None)
            ))
            left.add_widget(Label(
                text=f"  {detail}",
                font_size=DIMS['font_xs'],
                color=COLORS['text_dim'],
                halign='left',
                text_size=(200, None)
            ))
            card.add_widget(left)
            
            # Sag: status badge
            clr = COLORS['success'] if status == "Clean" else COLORS['warning']
            badge = Label(
                text=status,
                font_size=DIMS['font_xs'],
                color=clr,
                size_hint_x=0.3
            )
            card.add_widget(badge)
            
            self.ids.repo_list.add_widget(card)
    
    def do_push(self, msg):
        if not msg.strip():
            msg = "OWL auto-commit"
        self.git_status = "Pushing..."
        # Simulasyon
        def _done(dt):
            self.git_status = "Clean"
        Clock.schedule_once(_done, 1.5)
