import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt

# URL for your Auralis dashboard
DASHBOARD_URL = "http://localhost:8080/dashboard"

class Browser(QMainWindow):
    """
    A simple browser window to display the Auralis dashboard with zoom controls
    that correctly handles system display scaling.
    """
    def __init__(self, scale_factor=1.0):
        super().__init__()
        self.setWindowTitle("Auralis Dashboard")
        self.setGeometry(100, 100, 1200, 800)

        # *** THE KEY FIX ***
        # The application window will be scaled up by the OS (e.g., by 1.25).
        # The web content will ALSO be scaled up by the same factor, causing a
        # "double zoom". To fix this, we set a corrective zoom factor.
        # e.g., 1.0 / 1.25 = 0.8. When the 0.8 zoom is scaled up by 1.25, the
        # result is a perfect 1.0, matching Chrome's rendering.
        corrective_zoom = 1.0 / scale_factor if scale_factor > 0 else 1.0
        self.base_zoom = corrective_zoom
        self.current_zoom = self.base_zoom

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(DASHBOARD_URL))
        # Set the initial zoom factor to this new corrective value.
        self.browser.setZoomFactor(self.current_zoom)
        
        self.setCentralWidget(self.browser)
        self.showFullScreen()

    def keyPressEvent(self, event):
        """
        Handles key press events for shortcuts like fullscreen, reload, and zoom.
        """
        modifiers = event.modifiers()
        key = event.key()

        # Handle Ctrl key combinations
        if modifiers == Qt.ControlModifier:
            if key == Qt.Key_Plus or key == Qt.Key_Equal:
                # Zoom In (Ctrl + + or Ctrl + =)
                self.current_zoom += 0.1
                self.browser.setZoomFactor(self.current_zoom)
            elif key == Qt.Key_Minus:
                # Zoom Out (Ctrl + -)
                if self.current_zoom > 0.2:
                    self.current_zoom -= 0.1
                    self.browser.setZoomFactor(self.current_zoom)
            elif key == Qt.Key_0:
                # Reset Zoom (Ctrl + 0) to the corrective base zoom level.
                self.current_zoom = self.base_zoom
                self.browser.setZoomFactor(self.current_zoom)
            elif key == Qt.Key_R:
                # Reload Page (Ctrl + R)
                self.browser.reload()
            else:
                super().keyPressEvent(event)
        
        # Handle Fullscreen toggle
        elif key == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        else:
            super().keyPressEvent(event)

def run_browser():
    """
    Initializes and runs the Qt application.
    """
    # These settings are essential. They make the application window itself
    # aware of the OS scaling factor.
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    
    # Get the primary screen's device pixel ratio (e.g., 1.25 for 125%).
    screen = app.primaryScreen()
    scale_factor = screen.devicePixelRatio() if screen else 1.0

    # Pass the detected scale factor to the browser window to calculate
    # the corrective zoom.
    window = Browser(scale_factor=scale_factor)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_browser()

