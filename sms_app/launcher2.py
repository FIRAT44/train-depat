import sys
import os
import threading
import subprocess
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
)
from PySide6.QtCore import QUrl, QTimer
from PySide6.QtWebEngineWidgets import QWebEngineView

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt Embedded Browser")
        self.resize(1024, 768)

        # URL bar
        self.url_bar = QLineEdit(self)
        self.url_bar.setPlaceholderText("Enter URL and press Enter")
        self.url_bar.returnPressed.connect(self.load_url)

        # Go button
        self.go_button = QPushButton("Go", self)
        self.go_button.clicked.connect(self.load_url)

        # Local HTML button
        self.local_button = QPushButton("Open Local Page", self)
        self.local_button.clicked.connect(self.open_local)

        # Streamlit button
        self.streamlit_button = QPushButton("Open Streamlit App", self)
        self.streamlit_button.clicked.connect(self.open_streamlit)

        # Web view
        self.browser = QWebEngineView(self)
        self.browser.setUrl(QUrl("https://www.google.com"))

        # Layouts
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.url_bar)
        top_layout.addWidget(self.go_button)
        top_layout.addWidget(self.local_button)
        top_layout.addWidget(self.streamlit_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.server_thread = None
        self.streamlit_proc = None

    def load_url(self):
        url = self.url_bar.text().strip()
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        self.browser.setUrl(QUrl(url))

    def open_local(self):
        # Create example HTML
        html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset=\"utf-8\">
    <title>Local Example Page</title>
</head>
<body>
    <h1>Localhost Example</h1>
    <p>This is an example HTML file served locally.</p>
</body>
</html>
"""
        file_path = os.path.join(os.getcwd(), "example.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Start simple HTTP server
        if not self.server_thread:
            def serve():
                os.chdir(os.getcwd())
                with TCPServer(("", 8000), SimpleHTTPRequestHandler) as httpd:
                    httpd.serve_forever()
            self.server_thread = threading.Thread(target=serve, daemon=True)
            self.server_thread.start()

        # Load local page
        self.browser.setUrl(QUrl("http://127.0.0.1:8000/example.html"))

    def open_streamlit(self):
        # Start Streamlit app
        if not self.streamlit_proc:
            cmd = [
                "streamlit", "run", "streamlit_app.py",
                "--server.port", "8501",
                "--server.address", "127.0.0.1",
                "--server.headless", "true"
            ]
            self.streamlit_proc = subprocess.Popen(
                cmd,
                cwd=os.getcwd(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            # Wait a moment for server to start
            QTimer.singleShot(3000, lambda: self.browser.setUrl(QUrl("http://127.0.0.1:8501")))
        else:
            self.browser.setUrl(QUrl("http://127.0.0.1:8501"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec())
