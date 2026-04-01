cat > system_monitor.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监听模块 - 桌面AI助手的系统事件监听器
============================================

监听系统事件：
- 新软件安装（Linux dpkg/pacman日志）
- CPU和内存使用率
- 用户闲置时间

触发事件回调函数
"""

import os
import time
import threading
import platform
from typing import Dict, Any, Optional, Callable

try:
    import psutil
except ImportError:
    print("请先安装 psutil: pip install psutil")
    exit(1)

try:
    from pynput import mouse, keyboard
except ImportError:
    print("请先安装 pynput: pip install pynput")
    exit(1)


class SystemMonitor:
    """
    系统监听类
    监听系统事件并触发回调函数
    """

    def __init__(self, on_event: Callable[[str, Optional[Dict]], None]):
        """
        初始化系统监听器

        参数:
            on_event: 事件回调函数，接收 (event_name, data)
                事件类型：
                - 'new_install': 新软件安装，data包含 {'package': '包名'}
                - 'cpu_high': CPU使用率过高，data包含 {'usage': 百分比}
                - 'mem_high': 内存使用率过高，data包含 {'usage': 百分比}
                - 'user_idle': 用户闲置，data包含 {'idle_time': 秒数}
                - 'user_active': 用户恢复活动
        """
        self.on_event = on_event
        self._running = False
        self._threads = []

        # 检测操作系统
        self.os_type = platform.system().lower()
        print(f"[SystemMonitor] 检测到操作系统: {self.os_type}")

        # 防重复触发
        self._last_events = {
            'new_install': 0,
            'cpu_high': 0,
            'mem_high': 0,
            'user_idle': 0
        }

        # 用户闲置检测
        self._last_activity_time = time.time()
        self._was_idle = False

    def start(self):
        """启动所有监听线程"""
        if self._running:
            return

        self._running = True

        # 1. 软件安装监听线程
        install_thread = threading.Thread(target=self._monitor_install, daemon=True)
        install_thread.start()
        self._threads.append(install_thread)

        # 2. 资源监控线程
        resource_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        resource_thread.start()
        self._threads.append(resource_thread)

        # 3. 用户闲置输入监听
        self._start_idle_monitor()

        # 4. 闲置状态检测线程
        idle_check_thread = threading.Thread(target=self._check_idle, daemon=True)
        idle_check_thread.start()
        self._threads.append(idle_check_thread)

        print("[SystemMonitor] 所有监听线程已启动")

    def stop(self):
        """停止所有监听"""
        self._running = False
        print("[SystemMonitor] 正在停止监听...")

    # ==================== 软件安装监听 ====================

    def _monitor_install(self):
        """监听新软件安装"""
        if self.os_type == 'windows':
            self._monitor_install_windows()
        elif self.os_type == 'linux':
            self._monitor_install_linux()
        else:
            print(f"[SystemMonitor] 不支持的操作系统: {self.os_type}")

    def _monitor_install_linux(self):
        """Linux下监听软件安装"""
        log_files = []

        # Debian/Ubuntu
        if os.path.exists('/var/log/dpkg.log'):
            log_files.append(('/var/log/dpkg.log', 'install'))
        # Arch
        if os.path.exists('/var/log/pacman.log'):
            log_files.append(('/var/log/pacman.log', 'installed'))

        if not log_files:
            print("[SystemMonitor] 未找到软件安装日志文件")
            return

        positions = {}
        for log_file, _ in log_files:
            try:
                with open(log_file, 'rb') as f:
                    f.seek(0, os.SEEK_END)
                    positions[log_file] = f.tell()
            except:
                positions[log_file] = 0

        while self._running:
            for log_file, keyword in log_files:
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        f.seek(positions[log_file])
                        new_lines = f.readlines()
                        positions[log_file] = f.tell()

                        for line in new_lines:
                            if keyword in line:
                                package = self._extract_package_name(line, keyword)
                                if package:
                                    now = time.time()
                                    if now - self._last_events['new_install'] > 5:
                                        self._last_events['new_install'] = now
                                        self.on_event('new_install', {'package': package})
                except Exception as e:
                    pass

            time.sleep(1)

    def _monitor_install_windows(self):
        """Windows下监听软件安装（模拟）"""
        print("[SystemMonitor] Windows版待移植")
        while self._running:
            time.sleep(5)

    def _extract_package_name(self, line: str, keyword: str) -> Optional[str]:
        """从日志行提取包名"""
        import re
        if keyword == 'install':
            # dpkg.log: "2026-03-21 10:00:00 install python3:amd64"
            parts = line.split()
            if len(parts) >= 4:
                return parts[3]
        elif keyword == 'installed':
            # pacman.log: "[2026-03-21T10:00:00] [ALPM] installed python3"
            match = re.search(r'installed\s+(\S+)', line)
            if match:
                return match.group(1)
        return None

    # ==================== 资源监控 ====================

    def _monitor_resources(self):
        """监控CPU和内存使用率"""
        while self._running:
            try:
                # CPU使用率
                cpu = psutil.cpu_percent(interval=1)
                if cpu > 80:
                    now = time.time()
                    if now - self._last_events['cpu_high'] > 10:
                        self._last_events['cpu_high'] = now
                        self.on_event('cpu_high', {'usage': cpu})

                # 内存使用率
                mem = psutil.virtual_memory()
                mem_percent = mem.percent
                if mem_percent > 80:
                    now = time.time()
                    if now - self._last_events['mem_high'] > 10:
                        self._last_events['mem_high'] = now
                        self.on_event('mem_high', {'usage': mem_percent})

            except Exception as e:
                pass

            time.sleep(2)

    # ==================== 用户闲置监听 ====================

    def _start_idle_monitor(self):
        """启动输入事件监听"""
        def on_move(x, y):
            self._record_activity()
        def on_click(x, y, button, pressed):
            self._record_activity()
        def on_scroll(x, y, dx, dy):
            self._record_activity()
        def on_press(key):
            self._record_activity()

        mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
        mouse_listener.start()

        key_listener = keyboard.Listener(on_press=on_press)
        key_listener.start()

        self._listener_threads = [mouse_listener, key_listener]

    def _record_activity(self):
        """记录用户活动时间"""
        self._last_activity_time = time.time()
        if self._was_idle:
            self._was_idle = False
            self.on_event('user_active', None)

    def _check_idle(self):
        """检查用户闲置状态"""
        IDLE_TIMEOUT = 30 * 60  # 30分钟

        while self._running:
            idle_time = time.time() - self._last_activity_time

            if not self._was_idle and idle_time >= IDLE_TIMEOUT:
                self._was_idle = True
                self.on_event('user_idle', {'idle_time': idle_time})

            time.sleep(5)

    # ==================== 模拟事件（用于测试） ====================

    def simulate_install(self, package_name: str = "示例软件"):
        """模拟软件安装（用于测试）"""
        self.on_event('new_install', {'package': package_name})

    def simulate_cpu_high(self):
        """模拟CPU过高（用于测试）"""
        self.on_event('cpu_high', {'usage': 95})

    def simulate_idle(self):
        """模拟用户闲置（用于测试）"""
        self.on_event('user_idle', {'idle_time': 1800})


# ==================== 测试代码 ====================
if __name__ == "__main__":
    def test_callback(event_name, data):
        print(f"[事件] {event_name}: {data}")

    print("启动 SystemMonitor 测试...")
    monitor = SystemMonitor(on_event=test_callback)
    monitor.start()

    print("\n💡 提示：")
    print("  - 安装新软件时会触发 new_install")
    print("  - CPU/内存超80%会触发 cpu_high/mem_high")
    print("  - 30分钟无操作会触发 user_idle")
    print("  - 按 Ctrl+C 退出\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n停止测试...")
        monitor.stop()
EOF
