"""
Homepage / Welcome Screen for pycrosGUI
Part of the pycroscopy ecosystem

Features:
- Modern welcome screen with app branding
- Quick start button to launch main application
- Version info and credits
"""

try:
    from PyQt6 import QtWidgets, QtCore, QtGui
    from PyQt6.QtCore import Qt
except ImportError:
    from PyQt5 import QtWidgets, QtCore, QtGui
    from PyQt5.QtCore import Qt


class HomePage(QtWidgets.QWidget):
    """
    Modern homepage/welcome screen for pycrosGUI.
    """
    
    # Signal emitted when user clicks to enter main app
    enter_app = QtCore.pyqtSignal()
    
    def __init__(self, version="2025.1.1", parent=None):
        super().__init__(parent)
        self.version = version
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the homepage interface."""
        self.setWindowTitle("pycrosGUI - Welcome")
        self.setMinimumSize(800, 600)
        
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Background widget with gradient
        content = QtWidgets.QWidget()
        content.setObjectName("homepage_content")
        content.setStyleSheet("""
            #homepage_content {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2c3e50,
                    stop:0.5 #34495e,
                    stop:1 #1a252f
                );
            }
        """)
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(60, 40, 60, 40)
        
        # Top spacer (smaller to not cut off title)
        content_layout.addSpacing(20)
        
        # Logo/Title section
        title_container = QtWidgets.QWidget()
        title_container.setStyleSheet("background: transparent;")
        title_layout = QtWidgets.QVBoxLayout(title_container)
        title_layout.setSpacing(8)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main title
        title = QtWidgets.QLabel("pycrosGUI")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter if hasattr(Qt, 'AlignmentFlag') else Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 56px;
                font-weight: bold;
                font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
                background: transparent;
                padding: 10px;
            }
        """)
        title_layout.addWidget(title)
        
        # Subtitle
        subtitle = QtWidgets.QLabel("Python GUI for Microscopy")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter if hasattr(Qt, 'AlignmentFlag') else Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 22px;
                font-weight: 300;
                font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
                background: transparent;
            }
        """)
        title_layout.addWidget(subtitle)
        
        # Version
        version_label = QtWidgets.QLabel(f"Version {self.version}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter if hasattr(Qt, 'AlignmentFlag') else Qt.AlignCenter)
        version_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 13px;
                font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
                background: transparent;
            }
        """)
        title_layout.addWidget(version_label)
        
        content_layout.addWidget(title_container)
        
        # Spacer
        content_layout.addSpacing(10)
        
        # Description
        desc = QtWidgets.QLabel(
            "A comprehensive graphical interface for microscopy data analysis.\n"
            "Part of the pycroscopy ecosystem for scientific data processing."
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter if hasattr(Qt, 'AlignmentFlag') else Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet("""
            QLabel {
                color: #bdc3c7;
                font-size: 15px;
                font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
                background: transparent;
                padding: 10px 40px;
            }
        """)
        content_layout.addWidget(desc)
        
        # Spacer before features
        content_layout.addStretch(1)
        
        # Feature highlights
        features_container = QtWidgets.QWidget()
        features_container.setStyleSheet("background: transparent;")
        features_layout = QtWidgets.QHBoxLayout(features_container)
        features_layout.setSpacing(30)
        
        features = [
            ("📊", "Spectral Analysis", "EELS, EDS & spectroscopy"),
            ("🔬", "Image Processing", "Advanced microscopy tools"),
            ("🤖", "Agent Mode", "Autonomous S/TEM"),

        ]
        
        for icon, title, desc in features:
            feature = self._create_feature_card(icon, title, desc)
            features_layout.addWidget(feature)
        
        content_layout.addWidget(features_container)
        
        # Spacer
        content_layout.addSpacing(40)
        
        # Enter button
        enter_btn = QtWidgets.QPushButton("Enter Application")
        enter_btn.setCursor(QtGui.QCursor(Qt.CursorShape.PointingHandCursor if hasattr(Qt, 'CursorShape') else Qt.PointingHandCursor))
        enter_btn.setFixedSize(280, 60)
        enter_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 30px;
                font-size: 20px;
                font-weight: bold;
                font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f6aa5;
            }
        """)
        enter_btn.clicked.connect(self._on_enter)
        
        btn_container = QtWidgets.QWidget()
        btn_container.setStyleSheet("background: transparent;")
        btn_layout = QtWidgets.QHBoxLayout(btn_container)
        btn_layout.addStretch()
        btn_layout.addWidget(enter_btn)
        btn_layout.addStretch()
        content_layout.addWidget(btn_container)
        
        # Spacer at bottom
        content_layout.addStretch(1)
        
        # Footer with credits
        footer = QtWidgets.QLabel(
            "© 2025 Gerd Duscher & Levi Dunn  •  Pycroscopy Ecosystem  •  Open Source"
        )
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter if hasattr(Qt, 'AlignmentFlag') else Qt.AlignCenter)
        footer.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 12px;
                padding: 15px;
                font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
                background: transparent;
            }
        """)
        content_layout.addWidget(footer)
        
        main_layout.addWidget(content)
        
    def _create_feature_card(self, icon, title, desc):
        """Create a feature highlight card."""
        card = QtWidgets.QWidget()
        card.setFixedSize(170, 130)
        card.setObjectName("feature_card")
        card.setStyleSheet("""
            #feature_card {
                background-color: rgba(52, 73, 94, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(card)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 15, 12, 15)
        
        # Icon
        icon_label = QtWidgets.QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter if hasattr(Qt, 'AlignmentFlag') else Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                background: transparent;
            }
        """)
        layout.addWidget(icon_label)
        
        # Title
        title_label = QtWidgets.QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter if hasattr(Qt, 'AlignmentFlag') else Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QtWidgets.QLabel(desc)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter if hasattr(Qt, 'AlignmentFlag') else Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                font-size: 11px;
                background: transparent;
            }
        """)
        layout.addWidget(desc_label)
        
        return card
        
    def _on_enter(self):
        """Handle enter button click."""
        self.enter_app.emit()


# For standalone testing
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    home = HomePage()
    home.show()
    sys.exit(app.exec() if hasattr(app, 'exec') else app.exec_())
