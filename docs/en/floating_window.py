
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Floating Window Module - Desktop Overlay Window for AI Assistant
=================================================================

A transparent, always-on-top floating window that supports:
- Drag and drop movement
- System tray minimization
- Position and size memory
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSystemTrayIcon, QMenu, QMessageBox
)
from PyQt5.QtCore import Qt, QPoint, QSettings, QSize
from PyQt5.QtGui import QIcon, QColor, QPixmap, QFont
from PyQt5.QtWidgets import QDesktopWidget


class FloatingWindow(QWidget):
    """
    Custom floating window class.

    Features:
    - Translucent/transparent window
    - Always on top
    - Drag to move
    - System tray integration
    - Persistent position and size
    """

    def __init__(self):
        """Initialize floating window."""
        super().__init__()

        self.drag_pos = None
        self.is_dragging = False

        # Settings for persisting window state
        self.settings = QSettings('FloatingWindow', 'FloatingWindow')

        self.init_ui()
        self.create_tray()
        self.restore_window_state()

    def init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle('XiaoLin AI')

        # Set window size
        self.setGeometry(100, 100, 400, 300)

        # Set window flags
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

        # Set style
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 200);
                border-radius: 10px;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Title label
        title_label = QLabel('XiaoLin AI')
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white;")
        main_layout.addWidget(title_label)

        # Info label
        info_label = QLabel(
            '• Drag anywhere to move\n'
            '• Always on top\n'
            '• Minimize to tray\n'
            '• Right-click for menu'
        )
        info_label.setStyleSheet("color: #cccccc; line-height: 1.6;")
        main_layout.addWidget(info_label)

        main_layout.addStretch()

        # Button layout
        button_layout = QHBoxLayout()

        # Minimize button
        minimize_btn = QPushButton('Minimize to Tray')
        minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d47a1;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        minimize_btn.clicked.connect(self.hide_to_tray)
        button_layout.addWidget(minimize_btn)

        # Close button
        close_btn = QPushButton('Exit')
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #c62828;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        close_btn.clicked.connect(self.quit_app)
        button_layout.addWidget(close_btn)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def create_tray(self):
        """Create system tray icon and menu."""
        icon_pixmap = QPixmap(64, 64)
        icon_pixmap.fill(QColor(13, 71, 161, 255))
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(icon_pixmap))

        # Create tray menu
        tray_menu = QMenu(self)

        show_action = tray_menu.addAction('Show')
        show_action.triggered.connect(self.show_from_tray)

        tray_menu.addSeparator()

        about_action = tray_menu.addAction('About')
        about_action.triggered.connect(self.show_about)

        tray_menu.addSeparator()

        exit_action = tray_menu.addAction('Exit')
        exit_action.triggered.connect(self.quit_app)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_activated)
        self.tray_icon.show()

    def hide_to_tray(self):
        """Hide window to system tray."""
        self.hide()

    def show_from_tray(self):
        """Restore window from system tray."""
        self.showNormal()
        self.activateWindow()

    def tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason in (QSystemTrayIcon.DoubleClick, QSystemTrayIcon.Trigger):
            if self.isVisible():
                self.hide_to_tray()
            else:
                self.show_from_tray()

    def show_about(self):
        """Show about dialog."""
        QMessageBox.information(
            self,
            'About',
            'XiaoLin AI - Desktop AI Assistant\n\n'
            'Version: 1.0\n'
            'Powered by PyQt5\n'
            'Features: Floating window, system tray, always on top\n\n'
            'Part of the Qilin Republic project.'
        )

    def mousePressEvent(self, event):
        """Handle mouse press for dragging."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging."""
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.save_window_state()
            event.accept()

    def save_window_state(self):
        """Save window position and size."""
        self.settings.setValue('pos', self.pos())
        self.settings.setValue('size', self.size())

    def restore_window_state(self):
        """Restore window position and size."""
        pos = self.settings.value('pos')
        size = self.settings.value('size')

        if pos:
            self.move(pos)
        if size:
            self.resize(size)

        self.ensure_on_screen()

    def ensure_on_screen(self):
        """Ensure window is within screen bounds."""
        screen_geometry = QDesktopWidget().screenGeometry()

        x = self.x()
        y = self.y()
        w = self.width()
        h = self.height()

        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x + w > screen_geometry.width():
            x = screen_geometry.width() - w
        if y + h > screen_geometry.height():
            y = screen_geometry.height() - h

        self.move(x, y)

    def quit_app(self):
        """Exit application."""
        self.save_window_state()
        QApplication.quit()

    def closeEvent(self, event):
        """Handle close event - minimize to tray instead."""
        if self.tray_icon.isVisible():
            self.hide_to_tray()
            event.ignore()
        else:
            self.save_window_state()
            event.accept()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName('XiaoLin AI')
    app.setApplicationVersion('1.0')

    window = FloatingWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
