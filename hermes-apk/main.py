"""
Echo v5.3 - Anime & Film Öneri Sistemi
Kivy WebView Wrapper - Siyah ekran düzeltilmiş
"""
import os, sys, time, threading, socket

APP_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_PORT = 8765

def find_free_port():
    """Boş port bul."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def wait_for_server(port, timeout=15):
    """Server hazır olana bekle."""
    import urllib.request
    for _ in range(timeout * 2):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1)
            return True
        except:
            time.sleep(0.5)
    return False

# Kivy ayarları - import önce yapılmalı
os.environ['KIVY_LOG_LEVEL'] = 'warning'
os.environ['KIVY_WINDOW'] = 'sdl2'

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.webview import WebView

Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', False)

COLORS = {
    'bg': (0.03, 0.03, 0.06, 1),       # #08080f
    'surface': (0.07, 0.07, 0.09, 1),   # #111114
    'accent': (0.42, 0.36, 0.58, 1),    # #6b5b95
    'text': (0.78, 0.78, 0.78, 1),      # #c8c8c8
    'muted': (0.35, 0.35, 0.4, 1),      # #555566
    'neon': (0.3, 0.93, 0.92, 1),       # Lain cyan
}


class LoadingScreen(Screen):
    """Yükleniyor ekranı."""
    progress = NumericProperty(0)
    status = StringProperty("Başlatılıyor...")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=40, spacing=16)

        # Logo
        self.logo = Label(
            text="[b]ECHO[/b]",
            markup=True,
            font_size=36,
            color=COLORS['accent'],
            size_hint_y=0.3,
            halign='center'
        )
        self.layout.add_widget(self.logo)

        # Status
        self.status_label = Label(
            text="The Wired is everywhere...",
            font_size=14,
            color=COLORS['muted'],
            size_hint_y=0.2,
            halign='center'
        )
        self.layout.add_widget(self.status_label)

        # Progress bar
        self.pb = ProgressBar(max=100, value=0, size_hint_y=None, height=4)
        self.layout.add_widget(self.pb)

        self.add_widget(self.layout)

    def update_progress(self, value, text=""):
        self.progress = value
        self.pb.value = value
        if text:
            self.status = text
            self.status_label.text = text


class WebScreen(Screen):
    """WebView ekranı."""

    def __init__(self, url, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')

        # Nav bar
        nav = BoxLayout(size_hint_y=None, height=48, padding=(12, 4))
        nav.add_widget(Label(
            text="ECHO",
            font_size=18,
            color=COLORS['accent'],
            bold=True,
            size_hint_x=0.8,
            halign='left'
        ))
        self.status_dot = Label(
            text="●",
            font_size=12,
            color=COLORS['neon'],
            size_hint_x=0.2
        )
        nav.add_widget(self.status_dot)
        self.layout.add_widget(nav)

        # WebView
        self.webview = WebView(
            url=url,
            enable_javascript=True,
            enable_zoom=False,
            user_agent="Echo/5.3 Android"
        )
        self.layout.add_widget(self.webview)
        self.add_widget(self.layout)


class EchoApp(App):
    def build(self):
        self.title = "Echo"
        self.sm = ScreenManager()
        self.loading = LoadingScreen(name='loading')
        self.sm.add_widget(self.loading)
        self.sm.current = 'loading'

        # Server'ı arkada başlat
        Clock.schedule_once(self._start_server, 0.5)
        return self.sm

    def _start_server(self, dt):
        try:
            # Güncellenmiş oneri.py'yi import et
            sys.path.insert(0, os.path.join(APP_DIR, '..'))
            from oneri import start_web_server

            # Port bul
            port = find_free_port() if WEB_PORT is None else WEB_PORT
            self.port = port

            # Server'ı thread'de başlat
            self.server_thread = threading.Thread(
                target=start_web_server,
                args=(port,),
                daemon=True
            )
            self.server_thread.start()

            # Progress güncelle
            self.loading.update_progress(30, "Server başlatılıyor...")

            # Server hazır olana bekle
            Clock.schedule_once(lambda dt: self._wait_server(), 1)

        except Exception as e:
            self.loading.update_progress(0, f"Sunucu hatası: {e}")
            print(f"Server error: {e}")

    def _wait_server(self, dt=None):
        if wait_for_server(self.port, timeout=10):
            self.loading.update_progress(80, "Yükleniyor...")
            Clock.schedule_once(lambda dt: self._switch_to_web(), 0.5)
        else:
            self.loading.update_progress(50, "Server bekleniyor...")
            Clock.schedule_once(lambda dt: self._wait_server(), 1)

    def _switch_to_web(self):
        try:
            url = f"http://127.0.0.1:{self.port}/"
            self.web_screen = WebScreen(url=url, name='web')
            self.sm.add_widget(self.web_screen)
            self.sm.current = 'web'
            self.loading.update_progress(100, "Hazır!")
        except Exception as e:
            self.loading.update_progress(0, f"WebView hatası: {e}")

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == "__main__":
    EchoApp().run()
