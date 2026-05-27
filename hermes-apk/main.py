"""
Echo - Anime & Manga Oneri Sistemi
Kivy WebView Wrapper
"""
import os, sys, time, threading

APP_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_PORT = 8765

os.environ['KIVY_LOG_LEVEL'] = 'warning'

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar

Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', False)

COLORS = {
    'bg': (0.07, 0.07, 0.07, 1),
    'ice': (0.42, 0.36, 0.56, 1),
    'neon': (0.3, 0.93, 0.92, 1),
    'muted': (0.33, 0.33, 0.4, 1),
}

class EchoApp(App):
    server_status = StringProperty("Baslatiliyor...")
    is_ready = BooleanProperty(False)

    def build(self):
        self.title = "Echo"
        Window.clearcolor = COLORS['bg']
        root = BoxLayout(orientation='vertical')
        root.add_widget(self._build_nav())
        self.loading = BoxLayout(orientation='vertical', padding=40, spacing=20)
        self.status_label = Label(text="The Wired is everywhere...", font_size=18, color=COLORS['ice'], halign='center')
        self.loading.add_widget(self.status_label)
        self.pb = ProgressBar(max=100, value=0, size_hint_y=None, height=6)
        self.loading.add_widget(self.pb)
        root.add_widget(self.loading)
        Clock.schedule_once(self._start_server, 0)
        Clock.schedule_interval(self._check_server, 1)
        return root

    def _build_nav(self):
        nav = BoxLayout(size_hint_y=None, height=56, padding=8)
        nav.add_widget(Label(text="ECHO", font_size=20, color=COLORS['ice'], bold=True, size_hint_x=0.7))
        self.status_dot = Label(text="o", font_size=14, color=COLORS['muted'], size_hint_x=0.3)
        nav.add_widget(self.status_dot)
        return nav

    def _start_server(self, dt):
        try:
            sys.path.insert(0, APP_DIR)
            from oneri import start_web_server
            t = threading.Thread(target=start_web_server, args=(WEB_PORT,), daemon=True)
            t.start()
            self.server_status = "OK"
        except Exception as e:
            self.server_status = str(e)

    def _check_server(self, dt):
        self.pb.value += 20
        if self.pb.value >= 100:
            self._load_webview()
            return False

    def _load_webview(self):
        try:
            self.root.remove_widget(self.loading)
            self.status_dot.color = COLORS['neon']
            # Use pyjnius to create Android WebView
            try:
                from jnius import autoclass
                WebView = autoclass('android.webkit.WebView')
                WebSettings = autoclass('android.webkit.WebSettings')
                activity = autoclass('org.kivy.android.PythonActivity').mActivity
                webview = WebView(activity)
                webview.getSettings().setJavaScriptEnabled(True)
                webview.getSettings().setDomStorageEnabled(True)
                webview.loadUrl(f"http://127.0.0.1:{WEB_PORT}/")
                activity.setContentView(webview)
            except Exception as e:
                # Fallback: try kivy webview
                try:
                    from kivy.uix.webview import WebView as KVWebView
                    wv = KVWebView(url=f"http://127.0.0.1:{WEB_PORT}/", enable_javascript=True, enable_zoom=False)
                    self.root.add_widget(wv)
                except:
                    self.status_label.text = f"WebView error: {e}"
                    self.root.add_widget(self.status_label)
        except Exception as e:
            self.status_label.text = str(e)

    def on_pause(self):
        return True

    def on_resume(self):
        pass

if __name__ == "__main__":
    EchoApp().run()
