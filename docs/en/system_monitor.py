
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Monitor Module - System Event Listener for Desktop AI Assistant
======================================================================

Monitors system events:
- New software installation (Linux dpkg/pacman logs)
- CPU and memory usage
- User idle time

Triggers callbacks when events occur.
"""

import os
import time
import threading
import platform
from typing import Dict, Any, Optional, Callable

try:
    import psutil
except ImportError:
    print("Please install psutil: pip install psutil")
    exit(1)

try:
    from pynput import mouse, keyboard
except ImportError:
    print("Please install pynput: pip install pynput")
    exit(1)


class SystemMonitor:
    """
    System monitor class.
    Monitors system events and triggers callbacks.
    """

    def __init__(self, on_event: Callable[[str, Optional[Dict]], None]):
        """
        Initialize system monitor.

        Args:
            on_event: Event callback function receiving (event_name, data)
                Event types:
                - 'new_install': New software installed, data {'package': name}
                - 'cpu_high': CPU usage > 80%, data {'usage': percentage}
                - 'mem_high': Memory usage > 80%, data {'usage': percentage}
                - 'user_idle': User idle for 30 minutes, data {'idle_time': seconds}
                - 'user_active': User resumed activity
        """
        self.on_event = on_event
        self._running = False
        self._threads = []

        # Detect OS
        self.os_type = platform.system().lower()
        print(f"[SystemMonitor] Detected OS: {self.os_type}")

        # Prevent duplicate events
        self._last_events = {
            'new_install': 0,
            'cpu_high': 0,
            'mem_high': 0,
            'user_idle': 0
        }

        # User idle detection
        self._last_activity_time = time.time()
        self._was_idle = False

    def start(self):
        """Start all monitoring threads."""
        if self._running:
            return

        self._running = True

        # 1. Software installation monitor thread
        install_thread = threading.Thread(target=self._monitor_install, daemon=True)
        install_thread.start()
        self._threads.append(install_thread)

        # 2. Resource monitor thread
        resource_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        resource_thread.start()
        self._threads.append(resource_thread)

        # 3. User idle input listener
        self._start_idle_monitor()

        # 4. Idle state checker thread
        idle_check_thread = threading.Thread(target=self._check_idle, daemon=True)
        idle_check_thread.start()
        self._threads.append(idle_check_thread)

        print("[SystemMonitor] All monitoring threads started")

    def stop(self):
        """Stop all monitoring."""
        self._running = False
        print("[SystemMonitor] Stopping monitoring...")

    # ==================== Software Installation Monitor ====================

    def _monitor_install(self):
        """Monitor new software installation."""
        if self.os_type == 'windows':
            self._monitor_install_windows()
        elif self.os_type == 'linux':
            self._monitor_install_linux()
        else:
            print(f"[SystemMonitor] Unsupported OS: {self.os_type}")

    def _monitor_install_linux(self):
        """Monitor software installation on Linux."""
        log_files = []

        # Debian/Ubuntu
        if os.path.exists('/var/log/dpkg.log'):
            log_files.append(('/var/log/dpkg.log', 'install'))
        # Arch
        if os.path.exists('/var/log/pacman.log'):
            log_files.append(('/var/log/pacman.log', 'installed'))

        if not log_files:
            print("[SystemMonitor] No software installation logs found")
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
        """Monitor software installation on Windows (simulated)."""
        print("[SystemMonitor] Windows version not yet implemented")
        while self._running:
            time.sleep(5)

    def _extract_package_name(self, line: str, keyword: str) -> Optional[str]:
        """Extract package name from log line."""
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

    # ==================== Resource Monitor ====================

    def _monitor_resources(self):
        """Monitor CPU and memory usage."""
        while self._running:
            try:
                # CPU usage
                cpu = psutil.cpu_percent(interval=1)
                if cpu > 80:
                    now = time.time()
                    if now - self._last_events['cpu_high'] > 10:
                        self._last_events['cpu_high'] = now
                        self.on_event('cpu_high', {'usage': cpu})

                # Memory usage
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

    # ==================== User Idle Monitor ====================

    def _start_idle_monitor(self):
        """Start input event listeners."""
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
        """Record user activity time."""
        self._last_activity_time = time.time()
        if self._was_idle:
            self._was_idle = False
            self.on_event('user_active', None)

    def _check_idle(self):
        """Check user idle state."""
        IDLE_TIMEOUT = 30 * 60  # 30 minutes

        while self._running:
            idle_time = time.time() - self._last_activity_time

            if not self._was_idle and idle_time >= IDLE_TIMEOUT:
                self._was_idle = True
                self.on_event('user_idle', {'idle_time': idle_time})

            time.sleep(5)

    # ==================== Simulated Events for Testing ====================

    def simulate_install(self, package_name: str = "example"):
        """Simulate software installation (for testing)."""
        self.on_event('new_install', {'package': package_name})

    def simulate_cpu_high(self):
        """Simulate high CPU usage (for testing)."""
        self.on_event('cpu_high', {'usage': 95})

    def simulate_idle(self):
        """Simulate user idle (for testing)."""
        self.on_event('user_idle', {'idle_time': 1800})


# ==================== Test Code ====================
if __name__ == "__main__":
    def test_callback(event_name, data):
        print(f"[Event] {event_name}: {data}")

    print("Starting SystemMonitor test...")
    monitor = SystemMonitor(on_event=test_callback)
    monitor.start()

    print("\n💡 Hints:")
    print("  - Installing new software will trigger 'new_install'")
    print("  - CPU/memory > 80% will trigger 'cpu_high'/'mem_high'")
    print("  - 30 minutes of inactivity will trigger 'user_idle'")
    print("  - Press Ctrl+C to exit\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping test...")
        monitor.stop()
