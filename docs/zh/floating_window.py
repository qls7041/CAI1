cat > floating_window.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
悬浮窗模块 - 桌面AI助手的悬浮窗口
====================================

透明、始终置顶的悬浮窗，支持：
- 鼠标拖拽移动
- 最小化到系统托盘
- 记忆窗口位置和大小
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
    自定义悬浮窗类

    特性：
    - 半透明/透明窗口
    - 始终置顶
    - 支持鼠标拖拽移动
    - 集成系统托盘功能
    - 记忆窗口位置和大小
    """

    def __init__(self):
        """初始化悬浮窗"""
        super().__init__()

        self.drag_pos = None
        self.is_dragging = False

        # 保存窗口状态的配置对象
        self.settings = QSettings('FloatingWindow', 'FloatingWindow')

        self.init_ui()
        self.create_tray()
        self.restore_window_state()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('小麟 AI')

        # 设置窗口大小
        self.setGeometry(100, 100, 400, 300)

        # 设置窗口属性
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 200);
                border-radius: 10px;
            }
        """)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # 标题标签
        title_label = QLabel('小麟 AI')
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white;")
        main_layout.addWidget(title_label)

        # 说明标签
        info_label = QLabel(
            '• 拖拽窗口任意位置移动\n'
            '• 窗口始终保持在最前\n'
            '• 可最小化到托盘\n'
            '• 右键菜单访问功能'
        )
        info_label.setStyleSheet("color: #cccccc; line-height: 1.6;")
        main_layout.addWidget(info_label)

        # 弹性空间
        main_layout.addStretch()

        # 按钮布局
        button_layout = QHBoxLayout()

        # 最小化按钮
        minimize_btn = QPushButton('最小化到托盘')
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

        # 关闭按钮
        close_btn = QPushButton('退出')
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
        """创建系统托盘图标和菜单"""
        icon_pixmap = QPixmap(64, 64)
        icon_pixmap.fill(QColor(13, 71, 161, 255))
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(icon_pixmap))

        # 创建托盘菜单
        tray_menu = QMenu(self)

        show_action = tray_menu.addAction('显示')
        show_action.triggered.connect(self.show_from_tray)

        tray_menu.addSeparator()

        about_action = tray_menu.addAction('关于')
        about_action.triggered.connect(self.show_about)

        tray_menu.addSeparator()

        exit_action = tray_menu.addAction('退出')
        exit_action.triggered.connect(self.quit_app)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_activated)
        self.tray_icon.show()

    def hide_to_tray(self):
        """隐藏窗口到系统托盘"""
        self.hide()

    def show_from_tray(self):
        """从系统托盘恢复窗口显示"""
        self.showNormal()
        self.activateWindow()

    def tray_activated(self, reason):
        """处理托盘图标激活事件"""
        if reason in (QSystemTrayIcon.DoubleClick, QSystemTrayIcon.Trigger):
            if self.isVisible():
                self.hide_to_tray()
            else:
                self.show_from_tray()

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.information(
            self,
            '关于',
            '小麟 AI - 桌面AI助手\n\n'
            '版本: 1.0\n'
            '技术栈: PyQt5\n'
            '功能: 悬浮窗、系统托盘、窗口置顶\n\n'
            '麒麟共和国项目'
        )

    def mousePressEvent(self, event):
        """处理鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，实现窗口拖拽"""
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.save_window_state()
            event.accept()

    def save_window_state(self):
        """保存窗口位置和大小到配置文件"""
        self.settings.setValue('pos', self.pos())
        self.settings.setValue('size', self.size())

    def restore_window_state(self):
        """从配置文件恢复窗口位置和大小"""
        pos = self.settings.value('pos')
        size = self.settings.value('size')

        if pos:
            self.move(pos)
        if size:
            self.resize(size)

        self.ensure_on_screen()

    def ensure_on_screen(self):
        """确保窗口在屏幕范围内"""
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
        """退出应用程序"""
        self.save_window_state()
        QApplication.quit()

    def closeEvent(self, event):
        """处理窗口关闭事件，最小化到托盘而非关闭"""
        if self.tray_icon.isVisible():
            self.hide_to_tray()
            event.ignore()
        else:
            self.save_window_state()
            event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName('小麟 AI')
    app.setApplicationVersion('1.0')

    window = FloatingWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
EOF
