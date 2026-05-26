"""
OWL Anime & Film APK - WebView Wrapper
Kivy + WebView ile anime/film oneri sistemi
Lain temali cyberpunk UI
"""
import os, sys, json, subprocess, time

# Proje yolu
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "data", "recommender.db")
WEB_PORT = 8765

os.environ['KIVY_LOG_LEVEL'] = 'warning'

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty

Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', False)

# Renk paleti
COLORS = {
    'bg_dark': (0.04, 0.04, 0.06, 1),
    'bg_card': (0.08, 0.08, 0.12, 1),
    'primary': (0.42, 0.13, 0.66, 1),
    'primary_light': (0.66, 0.33, 0.97, 1),
    'secondary': (0.05, 0.65, 0.92, 1),
    'text': (0.89, 0.91, 0.95, 1),
    'text_dim': (0.39, 0.45, 0.55, 1),
    'danger': (0.94, 0.27, 0.27, 1),
    'success': (0.13, 0.77, 0.37, 1),
    'border': (0.15, 0.15, 0.22, 1),
}

DIMS = {
    'padding_sm': 4, 'padding_md': 8, 'padding_lg': 16,
    'radius_sm': 4, 'radius_md': 8, 'radius_lg': 12,
    'font_xs': 10, 'font_sm': 12, 'font_md': 14, 'font_lg': 18,
    'font_xl': 24, 'nav_height': 60, 'btn_height': 44,
}


class WebServer:
    """Arka planda web server calistirir."""
    process = None

    @classmethod
    def start(cls):
        """Web server'i baslat."""
        if cls.process:
            return
        try:
            # oneri.py web server'ini baslat
            oneri_path = os.path.join(APP_DIR, "oneri.py")
            if not os.path.exists(oneri_path):
                oneri_path = os.path.join(APP_DIR, "..", "anime-project", "oneri.py")
            cls.process = subprocess.Popen(
                [sys.executable, oneri_path, "--web", str(WEB_PORT)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            time.sleep(2)  # Server hazir olana kadar bekle
        except Exception as e:
            print(f"Web server error: {e}")

    @classmethod
    def stop(cls):
        """Web server'i durdur."""
        if cls.process:
            cls.process.terminate()
            cls.process = None

    @classmethod
    def is_running(cls):
        """Server calisiyor mu?"""
        if cls.process is None:
            return False
        return cls.process.poll() is None


class OWLApp(App):
    """Ana OWL APK uygulaması."""
    server_status = StringProperty("Başlatılıyor...")
    is_ready = BooleanProperty(False)

    def build(self):
        self.title = "OWL Anime & Film"
        Window.clearcolor = COLORS['bg_dark']

        # Web server baslat
        Clock.schedule_once(self._start_server, 0)

        # WebView icin kullanici arayuzu
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.progressbar import ProgressBar

        root = BoxLayout(orientation='vertical')
        root.add_widget(self._build_nav())

        # Yukleme ekrani
        self.loading_layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        self.status_label = Label(
            text="The Wired is everywhere...",
            font_size=DIMS['font_lg'],
            color=COLORS['text'],
            halign='center'
        )
        self.loading_layout.add_widget(self.status_label)

        self.pb = ProgressBar(max=100, value=0, size_hint_y=None, height=8)
        self.loading_layout.add_widget(self.pb)

        root.add_widget(self.loading_layout)

        # Durum guncellemesi
        Clock.schedule_interval(self._check_server, 1)

        return root

    def _build_nav(self):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        nav = BoxLayout(size_hint_y=None, height=DIMS['nav_height'], padding=8)
        with nav.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(rgba=COLORS['bg_card'])
            nav._bg = Rectangle(pos=nav.pos, size=nav.size)
        nav.bind(pos=lambda obj, val: setattr(nav._bg, 'pos', val))
        nav.bind(size=lambda obj, val: setattr(nav._bg, 'size', val))

        title = Label(
            text="◇ OWL",
            font_size=DIMS['font_lg'],
            color=COLORS['primary_light'],
            bold=True,
            size_hint_x=0.6
        )
        nav.add_widget(title)

        self.status_dot = Label(
            text="●",
            font_size=DIMS['font_md'],
            color=COLORS['text_dim'],
            size_hint_x=0.2
        )
        nav.add_widget(self.status_dot)

        return nav

    def _start_server(self, dt):
        """Web server baslat."""
        try:
            WebServer.start()
            self.server_status = "Web server baslatildi"
        except Exception as e:
            self.server_status = f"Hata: {e}"

    def _check_server(self, dt):
        """Server durumunu kontrol et ve WebView yukle."""
        if WebServer.is_running():
            self.pb.value += 25
            self.status_label.text = "Connecting to the Wired..."

            if self.pb.value >= 100:
                self.is_ready = True
                self._load_webview()
                return False  # Interval'i durdur
        else:
            self.status_label.text = "Server bekleniyor..."
            self.pb.value = max(0, self.pb.value - 5)

    def _load_webview(self):
        """WebViewi yukle."""
        try:
            self.status_dot.color = COLORS['success']
            self.status_label.text = "Yukleniyor..."

            # Loading ekranini kaldir
            self.root.remove_widget(self.loading_layout)

            # WebView ekle
            try:
                from kivy.uix.webview import WebView
                webview = WebView(
                    url=f"http://127.0.0.1:{WEB_PORT}/",
                    enable_javascript=True,
                    enable_zoom=False
                )
                self.root.add_widget(webview)
            except ImportError:
                # Kivy WebView yoksa, pyclipper ile dene
                try:
                    from android.webkit import WebView as AndroidWebView
                    # Native Android WebView kullan
                    self.status_label.text = "Native WebView yukleniyor..."
                except:
                    self.status_label.text = "WebView desteklenmiyor"

        except Exception as e:
            self.status_label.text = f"Hata: {e}"
            self.status_dot.color = COLORS['danger']

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def on_stop(self):
        WebServer.stop()


if __name__ == "__main__":
    OWLApp().run()
