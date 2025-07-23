# launcher.py
import sys, os, socket, webbrowser, json
from pathlib import Path
from datetime import datetime
import requests

from dotenv import load_dotenv
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QLabel, QVBoxLayout, QHBoxLayout, QWidget,
    QMessageBox, QDialog, QLineEdit, QFormLayout,
    QGroupBox, QCalendarWidget, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QProcess, QSize, QUrl
from PySide6.QtGui import QPixmap, QIcon

from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QTabWidget


# .env yükleme
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR.parent / ".env")

# Credentials yükleme
def load_credentials():
    import json
    #SHARE_PATH = Path(r"\\Ayjetfile\shared\SMS\1400-SMS PROGRAM")
    #cred_file = SHARE_PATH / "credentials.json"
    cred_file ="credentials.json"



    try:
        with open(cred_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("username"), data.get("password")
    except Exception as e:
        print(f"⚠️ Credentials yüklenemedi: {e}")
    return None, None

ADMIN_USER, ADMIN_PASS = load_credentials()

# Kullanıcı bilgilerini JSON dosyasından al
def load_user_info(username):
    import json
    #SHARE_PATH = Path(r"\\Ayjetfile\shared\SMS\1400-SMS PROGRAM")
    #json_file = SHARE_PATH / "users.json"
    json_file ="users.json"
    try:
        with open(json_file, "r", encoding="utf-8") as jf:
            data = json.load(jf)
            return data.get(username, {"full_name": "Bilinmiyor", "department": "Bilinmiyor"})
    except Exception as e:
        print(f"⚠️ Kullanıcı bilgisi yüklenemedi: {e}")
    return {"full_name": "Bilinmiyor", "department": "Bilinmiyor"}

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AYJET SMS-CMS Giriş")
        self.setFixedSize(480, 650)
        self.setStyleSheet("""
            QDialog { background-color: #F0F4F8; }
            QLabel#title { font-size: 24px; font-weight: bold; color: #1E88E5; }
            QLabel { color: #2C3E50; }
            QLineEdit { background-color: #FFFFFF; border: 2px solid #DDD; border-radius: 12px; padding: 8px; font-size: 14px; color: #333; }
            QLineEdit:focus { border-color: #1E88E5; }
            QPushButton { background-color: #1E88E5; color: #FFF; border-radius: 12px; padding: 10px; font-size: 16px; }
            QPushButton:hover { background-color: #1565C0; }
            QGroupBox { font-weight: bold; color: #1E88E5; border: 1px solid #DDD; border-radius: 8px; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; }
        """)
        # Logo ve Bildirim
        header = QHBoxLayout()
        logo = QLabel()
        logo_path = BASE_DIR / "resources" / "logo.png"
        if logo_path.exists():
            pix = QPixmap(str(logo_path)).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo.setPixmap(pix)
            logo.setFixedSize(pix.size())
        header.addWidget(logo, alignment=Qt.AlignLeft)
       

        # Başlık
        title = QLabel("AYJET SMS-CMS DEPARTMAN")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        # Giriş Formu
        self.user_edit = QLineEdit(); self.user_edit.setPlaceholderText("Kullanıcı Adı")
        self.pass_edit = QLineEdit(); self.pass_edit.setPlaceholderText("Parola"); self.pass_edit.setEchoMode(QLineEdit.Password)
        form_layout = QFormLayout(); form_layout.setContentsMargins(50,0,50,0); form_layout.setSpacing(20)
        form_layout.addRow(self.user_edit)
        form_layout.addRow(self.pass_edit)
        btn_login = QPushButton("Giriş Yap"); btn_login.setFixedHeight(45); btn_login.clicked.connect(self._check_credentials)

        # Düzen
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20); layout.setSpacing(15)
        layout.addLayout(header)
        layout.addWidget(title)
        layout.addLayout(form_layout)
        layout.addWidget(btn_login, alignment=Qt.AlignCenter)
   
    def _check_credentials(self):
        user = self.user_edit.text().strip()
        pwd = self.pass_edit.text().strip()
        if user == ADMIN_USER and pwd == ADMIN_PASS:
            self.accept()
        else:
            QMessageBox.warning(self, "Hata", "Geçersiz kullanıcı adı veya parola")
class WebWindow(QMainWindow):
    def __init__(self, title: str, url: str):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(1200, 800)
        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)
        self.web_view.load(QUrl(url))



# — Helper: correct script path for PyInstaller —
def _script_path(filename: str) -> str:
    if getattr(sys, '_MEIPASS', None):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent
    return str((base / filename).resolve())

# — WebWindow: ayrı Qt penceresinde Streamlit göstermek için —
class WebWindow(QMainWindow):
    def __init__(self, title: str, url: str):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(1200, 800)
        view = QWebEngineView()
        self.setCentralWidget(view)
        view.load(QUrl(url))

class WebWindow(QMainWindow):
    def __init__(self, title: str, url: str):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(1200, 800)
        view = QWebEngineView()
        self.setCentralWidget(view)
        view.load(QUrl(url))

class MainWindow(QMainWindow):
    def __init__(self, username: str):
        super().__init__()
        self.username = username
        self.setWindowTitle("✨ AYJET SMS-CMS Paneli")
        self.resize(1000, 700)

                # Başlamamış portlar
        self.sms_port = None
        self.cms_port = None
        self._sms_proc = None
        self._cms_proc = None
        self.sms_window = None
        self.cms_window = None

        # Sistem durumu görüntüsü
        status_g = QGroupBox("⚙️ Sistem Durumu")
        sg = QFormLayout(status_g)
        self.server_lbl = QLabel()
        self.sync_lbl = QLabel()
        sg.addRow("Sunucu:", self.server_lbl)
        sg.addRow("Son Senkron:", self.sync_lbl)
        self._refresh_system_status()
        QTimer(self, timeout=self._refresh_system_status).start(5000)

        # Sekmeler: SMS ve CMS başlatma butonları
        self.tabs = QTabWidget()
        for label, handler in [("SMS", self.start_streamlit_sms), ("CMS", self.start_streamlit_cms)]:
            tab = QWidget()
            lay = QVBoxLayout(tab)
            btn = QPushButton(f"🚀 {label} Başlat ve Göster")
            btn.clicked.connect(handler)
            lay.addWidget(btn)
            self.tabs.addTab(tab, label)

        # Sistem durumu ve başlat butonu
        status_g = QGroupBox("⚙️ Sistem Durumu")
        sg = QFormLayout(status_g)
        self.server_lbl = QLabel()
        self.sync_lbl = QLabel()
        sg.addRow("Sunucu:", self.server_lbl)
        sg.addRow("Son Senkron:", self.sync_lbl)
        self.btn_server_start = QPushButton("▶️ Sunucuyu Başlat")
        self.btn_server_start.clicked.connect(self.start_streamlit_sms)
        self.btn_server_start.setVisible(False)
        sg.addRow("", self.btn_server_start)
        self._refresh_system_status()
        QTimer(self, timeout=self._refresh_system_status).start(5000)

        # Diğer kontroller
        calendar = QCalendarWidget()
        calendar.setGridVisible(True)
        calendar.setFixedHeight(200)

        manual_grp = QGroupBox("Manualler ve Versiyonları")
        mg = QVBoxLayout(manual_grp)
        mg.addWidget(QPushButton("Doküman Kütüphanesi"))
        mg.addWidget(QPushButton("Versiyon Geçmişi"))

        user_info = load_user_info(self.username)
        user_g = QGroupBox("👤 Kişi Bilgileri")
        ug = QFormLayout(user_g)
        ug.addRow("Ad Soyad:", QLabel(user_info["full_name"]))
        ug.addRow("Departman:", QLabel(user_info["department"]))
        ug.addRow("Kullanıcı Adı:", QLabel(self.username))

        footer = QLabel("© 2025 Ayjet Flight School", alignment=Qt.AlignCenter)

        main_lay = QVBoxLayout()
        main_lay.addWidget(self.tabs, stretch=1)
        main_lay.addWidget(calendar)
        main_lay.addWidget(manual_grp)
        main_lay.addWidget(user_g)
        main_lay.addWidget(status_g)
        main_lay.addWidget(footer)

        container = QWidget()
        container.setLayout(main_lay)
        self.setCentralWidget(container)

    def _refresh_system_status(self):
        """
        Başlatılmış SMS veya CMS sunucularının herhangi birinin durumunu kontrol eder.
        Önce hangi portlar başlatıldıysa onları dener.
        """
        hosts = ["127.0.0.1", socket.gethostbyname(socket.gethostname())]
        # Kontrol edilecek portlar
        ports = []
        if self.sms_port:
            ports.append(self.sms_port)
        if self.cms_port:
            ports.append(self.cms_port)
        # Henüz başlatılmadıysa bilgi ver
        if not ports:
            self.server_lbl.setText("Henüz başlatılmadı")
        else:
            up = False
            for port in ports:
                for h in hosts:
                    try:
                        with socket.create_connection((h, port), timeout=0.5):
                            up = True
                            break
                    except OSError:
                        continue
                if up:
                    break
            self.server_lbl.setText("Çalışıyor" if up else "Kapalı")
        # Zaman bilgisini güncelle
        self.sync_lbl.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def _get_free_port(self) -> int:
        s = socket.socket()
        s.bind(("", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    def _wait_for_port(self, port: int, callback, retries: int = 20):
        try:
            sock = socket.create_connection(("127.0.0.1", port), timeout=0.2)
            sock.close()
            callback()
        except OSError:
            if retries <= 0:
                QMessageBox.critical(self, "Hata", f"Sunucu {port} portunda başlatılamadı.")
            else:
                QTimer.singleShot(500, lambda: self._wait_for_port(port, callback, retries-1))

    def start_streamlit_sms(self):
        cmd = sys.executable
        script = _script_path("streamlit_app.py")
        args = [
            "-m", "streamlit", "run", script,
            "--server.address", "127.0.0.1",
            "--server.port", str(self.sms_port),
            "--server.headless", "true",
        ]
        self._sms_proc = QProcess(self)
        self._sms_proc.start(cmd, args)
        if not self._sms_proc.waitForStarted(10000):
            QMessageBox.critical(self, "Hata", "SMS sunucusu başlatılamadı!")
            return
        # Pencereyi aç
        self.sms_window = WebWindow("SMS Uygulaması", f"http://127.0.0.1:{self.sms_port}")
        self.sms_window.show()

        
    def _show_sms_window(self):
        url = f"http://127.0.0.1:{self.sms_port}"
        self.sms_window = WebWindow("SMS Uygulaması", url)
        self.sms_window.show()

    def start_streamlit_cms(self):
        if self.cms_port is None:
            self.cms_port = self._get_free_port()
        cmd = sys.executable
        script = _script_path("cms_app.py")
        args = ["-m", "streamlit", "run", script,
                "--server.address", "0.0.0.0",
                "--server.port", str(self.cms_port),
                "--server.headless", "true"]
        self._cms_proc = QProcess(self)
        self._cms_proc.setWorkingDirectory(Path(script).parent.as_posix())
        self._cms_proc.readyReadStandardOutput.connect(
            lambda: print(self._cms_proc.readAllStandardOutput().data().decode(), end="")
        )
        self._cms_proc.readyReadStandardError.connect(
            lambda: print(self._cms_proc.readAllStandardError().data().decode(), end="")
        )
        self._cms_proc.start(cmd, args)
        if not self._cms_proc.waitForStarted(3000):
            QMessageBox.critical(self, "Hata", "CMS süreci başlatılamadı!")
            return
        self._wait_for_port(self.cms_port, self._show_cms_window)

    def _show_cms_window(self):
        url = f"http://127.0.0.1:{self.cms_port}"
        self.cms_window = WebWindow("CMS Uygulaması", url)
        self.cms_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginDialog()
    if login.exec() == QDialog.Accepted:
        win = MainWindow(login.user_edit.text().strip())
        win.show()
        sys.exit(app.exec())