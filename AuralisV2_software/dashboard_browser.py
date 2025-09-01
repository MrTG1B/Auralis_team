import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt

DASHBOARD_URL = "http://localhost:8080/dashboard"

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auralis Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(DASHBOARD_URL))
        self.browser.setZoomFactor(1.0)  # Ensure normal zoom
        self.setCentralWidget(self.browser)
        self.showFullScreen()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        elif event.key() == Qt.Key_R and event.modifiers() & Qt.ControlModifier:
            self.browser.reload()
        else:
            super().keyPressEvent(event)

def run_browser():
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec_())