"""
Echo v5.3 - Anime & Film Öneri Sistemi
Android APK - Native WebView (pyjnius)
Siyah ekran sorunu düzeltilmiş, kivy.uix.webview KULLANILMIYOR.
"""
import os, sys, time, threading, socket

# APK içinde yol yapısı:
# source.dir=.. ile: app/oneri.py, app/data/, app/hermes-apk/main.py
# APP_DIR = .../app/hermes-apk/  → PARENT_DIR = .../app/  (oneri.py burada)
APP_DIR    = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(APP_DIR)
sys.path.insert(0, PARENT_DIR)   # oneri.py için
sys.path.insert(0, APP_DIR)      # hermes-apk/ içindeki modüller için

WEB_PORT = 8765

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def wait_for_server(port, timeout=20):
    import urllib.request
    for _ in range(timeout * 4):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1)
            return True
        except:
            time.sleep(0.25)
    return False

# Android kontrolü
ANDROID = os.path.exists('/data/data')

os.environ['KIVY_LOG_LEVEL'] = 'warning'

from kivy.app import App
from kivy.config import Config
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Rectangle

Config.set('graphics', 'resizable', False)

COLORS = {
    'bg':      (0.04, 0.04, 0.06, 1),
    'accent':  (0.42, 0.36, 0.58, 1),
    'text':    (0.78, 0.78, 0.78, 1),
    'muted':   (0.33, 0.33, 0.40, 1),
    'neon':    (0.30, 0.93, 0.92, 1),
}


class LoadingScreen(Screen):
    progress = NumericProperty(0)
    status   = StringProperty("Başlatılıyor...")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*COLORS['bg'])
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

        layout = BoxLayout(orientation='vertical', padding=48, spacing=20)

        layout.add_widget(Label(
            text="[b]ECHO[/b]",
            markup=True,
            font_size='38sp',
            color=COLORS['accent'],
            size_hint_y=0.35,
            halign='center',
            valign='middle',
        ))

        layout.add_widget(Label(
            text="Anime & Film Öneri",
            font_size='13sp',
            color=COLORS['muted'],
            size_hint_y=0.10,
            halign='center',
        ))

        self.status_label = Label(
            text=self.status,
            font_size='12sp',
            color=COLORS['muted'],
            size_hint_y=0.10,
            halign='center',
        )
        layout.add_widget(self.status_label)

        self.pb = ProgressBar(max=100, value=0, size_hint_y=None, height='6dp')
        layout.add_widget(self.pb)

        layout.add_widget(Label(
            text="The Wired is everywhere...",
            font_size='10sp',
            color=(0.20, 0.20, 0.25, 1),
            size_hint_y=0.35,
            halign='center',
        ))
        self.add_widget(layout)

    def _update_rect(self, *args):
        self._rect.pos  = self.pos
        self._rect.size = self.size

    def update_progress(self, value, text=""):
        self.pb.value = value
        if text:
            self.status_label.text = text


class EchoApp(App):
    def build(self):
        self.title = "Echo"
        self.sm = ScreenManager()
        self.loading = LoadingScreen(name='loading')
        self.sm.add_widget(self.loading)
        self.sm.current = 'loading'
        self._port = WEB_PORT
        Clock.schedule_once(self._start_server, 0.8)
        return self.sm

    def _start_server(self, dt):
        self.loading.update_progress(10, "Veritabanı yükleniyor...")
        try:
            from oneri import start_web_server
        except ImportError as e:
            self.loading.update_progress(0, f"Import hatası: {e}")
            return

        self.loading.update_progress(25, "Server başlatılıyor...")
        t = threading.Thread(
            target=start_web_server,
            args=(self._port,),
            daemon=True,
        )
        t.start()
        Clock.schedule_once(self._check_server, 1.0)

    def _check_server(self, dt):
        self.loading.update_progress(50, "Bağlantı bekleniyor...")
        def _run():
            ok = wait_for_server(self._port, timeout=20)
            Clock.schedule_once(
                lambda dt: self._on_server_ready(ok), 0
            )
        threading.Thread(target=_run, daemon=True).start()

    def _on_server_ready(self, ok):
        if not ok:
            self.loading.update_progress(40, "Server hazırlanıyor...")
            Clock.schedule_once(self._check_server, 2.0)
            return

        self.loading.update_progress(85, "Arayüz yükleniyor...")
        url = f"http://127.0.0.1:{self._port}/"
        Clock.schedule_once(lambda dt: self._open_webview(url), 0.3)

    def _open_webview(self, url):
        if ANDROID:
            self._open_android_webview(url)
        else:
            self._open_desktop_fallback(url)

    def _open_android_webview(self, url):
        """Gerçek Android native WebView - pyjnius ile."""
        try:
            from jnius import autoclass, cast
            from android.runnable import run_on_ui_thread

            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            WebView        = autoclass('android.webkit.WebView')
            WebViewClient  = autoclass('android.webkit.WebViewClient')
            LayoutParams   = autoclass('android.view.ViewGroup$LayoutParams')
            Color          = autoclass('android.graphics.Color')

            activity = PythonActivity.mActivity

            @run_on_ui_thread
            def _create():
                wv = WebView(activity)
                wv.setBackgroundColor(Color.parseColor("#0a0a0f"))

                settings = wv.getSettings()
                settings.setJavaScriptEnabled(True)
                settings.setDomStorageEnabled(True)
                settings.setLoadWithOverviewMode(True)
                settings.setUseWideViewPort(True)
                settings.setBuiltInZoomControls(False)
                settings.setDisplayZoomControls(False)
                settings.setCacheMode(1)  # LOAD_DEFAULT

                wv.setWebViewClient(WebViewClient())
                wv.loadUrl(url)

                lp = LayoutParams(
                    LayoutParams.MATCH_PARENT,
                    LayoutParams.MATCH_PARENT,
                )
                activity.addContentView(wv, lp)

            _create()
            self.loading.update_progress(100, "Hazır!")

        except Exception as e:
            self.loading.update_progress(0, f"WebView hatası: {e}")
            print(f"[Echo] Android WebView error: {e}")

    def _open_desktop_fallback(self, url):
        """Masaüstü/test için basit URL gösterimi."""
        from kivy.uix.label import Label
        fallback = Screen(name='web')
        with fallback.canvas.before:
            from kivy.graphics import Color as KColor, Rectangle as KRect
            KColor(0.04, 0.04, 0.06, 1)
            r = KRect(pos=fallback.pos, size=fallback.size)
        lbl = Label(
            text=f"[b]ECHO[/b] çalışıyor\n\n[color=#6b5b95]{url}[/color]",
            markup=True,
            halign='center',
            font_size='14sp',
            color=(0.78, 0.78, 0.78, 1),
        )
        fallback.add_widget(lbl)
        self.sm.add_widget(fallback)
        self.sm.current = 'web'
        self.loading.update_progress(100, "Hazır!")

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == "__main__":
    EchoApp().run()
