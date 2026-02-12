#!/usr/bin/python3
import sys
import subprocess
import os
import re
import requests
import time
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QLabel, QComboBox, QHBoxLayout, QInputDialog, QMessageBox)
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal

CONFIG_DIR    = os.path.expanduser("~/vpn-configs")
APP_DIR       = os.path.expanduser("~/.config/mini-vpn")
FIRST_RUN_FLAG = os.path.join(APP_DIR, ".first_run_done")
AUTOSTART_DIR  = os.path.expanduser("~/.config/autostart")
AUTOSTART_FILE = os.path.join(AUTOSTART_DIR, "mini-vpn.desktop")
SCRIPT_PATH    = os.path.abspath(__file__)


def check_first_run(app: QApplication):
    if os.path.exists(FIRST_RUN_FLAG):
        return

    os.makedirs(APP_DIR, exist_ok=True)

    py_deps = ["python-pyqt6", "python-requests"]

    msg = QMessageBox()
    msg.setWindowTitle("Первый запуск")
    msg.setIcon(QMessageBox.Icon.Question)
    msg.setText(
        "<b>Похоже, это первый запуск Mini VPN.</b><br><br>"
        "Для работы GUI нужны следующие пакеты:<br>"
        f"<code>{'  '.join(py_deps)}</code><br><br>"
        "Установить сейчас?"
    )
    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg.setDefaultButton(QMessageBox.StandardButton.Yes)

    if msg.exec() == QMessageBox.StandardButton.Yes:
        cmd = f"sudo pacman -S --needed --noconfirm {' '.join(py_deps)}"
        subprocess.run([
            'konsole', '-e', 'sh', '-c',
            f"echo 'Устанавливаю GUI-зависимости...'; {cmd}; echo; echo 'Готово! Закрываю через 2 сек...'; sleep 2"
        ])

    with open(FIRST_RUN_FLAG, 'w') as f:
        f.write("done\n")

def comment_dns_in_config(conf_path: str) -> bool:
    try:
        with open(conf_path, 'r') as f:
            lines = f.readlines()

        new_lines = []
        changed = False
        for line in lines:
            if re.match(r'^\s*DNS\s*=', line, re.IGNORECASE):
                new_lines.append('# ' + line)
                changed = True
            else:
                new_lines.append(line)

        if changed:
            with open(conf_path, 'w') as f:
                f.writelines(new_lines)
        return changed
    except Exception as e:
        print(f"[DNS patch] Ошибка: {e}")
        return False

class MonitorThread(QThread):
    info_updated = pyqtSignal(str, str)

    def run(self):
        while True:
            ip   = "Ошибка"
            ping = "---"
            try:
                r = requests.get('https://api.ipify.org', timeout=3)
                if r.status_code == 200:
                    ip = r.text.strip()
                p = subprocess.run(['ping', '-c', '1', '-W', '1', '1.1.1.1'],
                                   capture_output=True, text=True)
                if p.returncode == 0:
                    ping = p.stdout.split('time=')[1].split(' ms')[0]
            except:
                pass
            self.info_updated.emit(ip, ping)
            time.sleep(7)

class UltimateVPN(QWidget):
    def __init__(self):
        super().__init__()
        self.current_ip = "Определяется..."
        self.ip_hidden  = True

        os.makedirs(CONFIG_DIR, exist_ok=True)

        self.initUI()

        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1500)

        self.monitor = MonitorThread()
        self.monitor.info_updated.connect(self.handle_info_update)
        self.monitor.start()

        self.refresh_autostart_btn()

    def initUI(self):
        self.setWindowTitle('Arch VPN Pro')
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1b26;
                color: #a9b1d6;
                font-family: 'Cantarell', sans-serif;
            }
            QPushButton {
                border-radius: 6px; padding: 10px;
                font-weight: bold; background-color: #444b6a; color: white;
            }
            QPushButton:hover { background-color: #565f89; }
            QComboBox {
                background-color: #24283b; border: 1px solid #414868;
                padding: 5px; color: white;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(6)

        self.status_card = QLabel("СИСТЕМА ГОТОВА")
        self.status_card.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_card.setStyleSheet("""
            background-color: #414868; color: white; font-size: 15px;
            font-weight: bold; border-radius: 10px; padding: 12px;
        """)
        layout.addWidget(self.status_card)

        self.ip_display = QPushButton("ВАШ IP: ••••••••••••••")
        self.ip_display.setFlat(True)
        self.ip_display.clicked.connect(self.toggle_ip_visibility)
        self.ip_display.setStyleSheet("""
            color: #7aa2f7; font-size: 14px; font-weight: bold;
            border: none; background: transparent; padding: 5px;
        """)
        layout.addWidget(self.ip_display)

        self.ping_label = QLabel("Ping: --- ms")
        self.ping_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ping_label.setStyleSheet("color: #bb9af7;")
        layout.addWidget(self.ping_label)

        layout.addWidget(QLabel("Выберите сервер:"))
        cfg_layout = QHBoxLayout()
        self.combo = QComboBox()
        self.refresh_configs()
        cfg_layout.addWidget(self.combo, 4)

        btn_rename = QPushButton("📝")
        btn_rename.setToolTip("Переименовать конфиг")
        btn_rename.clicked.connect(self.rename_config)
        btn_rename.setFixedWidth(40)
        cfg_layout.addWidget(btn_rename)

        btn_open = QPushButton("📂")
        btn_open.setToolTip("Открыть папку конфигов")
        btn_open.clicked.connect(lambda: subprocess.run(['xdg-open', CONFIG_DIR]))
        btn_open.setFixedWidth(40)
        cfg_layout.addWidget(btn_open)
        layout.addLayout(cfg_layout)

        layout.addStretch()

        btn_dns = QPushButton("🔇 ЗАКОММЕНТИРОВАТЬ DNS В КОНФИГЕ")
        btn_dns.setToolTip("Добавляет # перед строкой DNS= в выбранном конфиге")
        btn_dns.clicked.connect(self.patch_dns)
        btn_dns.setStyleSheet("background-color: #2d4f67; color: #7dcfff;")
        layout.addWidget(btn_dns)

        btn_deps = QPushButton("🛠 УСТАНОВИТЬ ЗАВИСИМОСТИ")
        btn_deps.clicked.connect(self.install_deps)
        btn_deps.setStyleSheet("background-color: #3d59a1; color: white;")
        layout.addWidget(btn_deps)

        self.btn_autostart = QPushButton("🔁 ДОБАВИТЬ В АВТОЗАГРУЗКУ")
        self.btn_autostart.clicked.connect(self.toggle_autostart)
        self.btn_autostart.setStyleSheet("background-color: #1f4b3a; color: #9ece6a;")
        layout.addWidget(self.btn_autostart)

        self.btn_up = QPushButton("⚡ ВКЛЮЧИТЬ VPN")
        self.btn_up.clicked.connect(self.connect_vpn)
        self.btn_up.setStyleSheet(
            "background-color: #9ece6a; color: #1a1b26; height: 50px; font-size: 14px;"
        )
        layout.addWidget(self.btn_up)

        self.btn_down = QPushButton("🛑 ВЫКЛЮЧИТЬ VPN")
        self.btn_down.clicked.connect(self.disconnect_all)
        self.btn_down.setStyleSheet("background-color: #f7768e; color: #1a1b26; height: 40px;")
        layout.addWidget(self.btn_down)

        self.setLayout(layout)

    def install_deps(self):
        pkgs = ["wireguard-tools", "openresolv", "wgcf", "python-requests"]
        if QMessageBox.question(
            self, 'Установка зависимостей', f"Установить пакеты?\n{', '.join(pkgs)}"
        ) == QMessageBox.StandardButton.Yes:
            cmd = f"sudo pacman -S --needed --noconfirm {' '.join(pkgs)}"
            subprocess.run([
                'konsole', '-e', 'sh', '-c',
                f"echo 'Ставлю пакеты...'; {cmd}; echo 'Готово!'; sleep 2"
            ])

    def patch_dns(self):
        selected = self.combo.currentText()
        if not selected or "Пусто" in selected:
            QMessageBox.warning(self, "DNS патч", "Сначала выберите конфиг.")
            return

        conf_path = os.path.join(CONFIG_DIR, f"{selected}.conf")
        if not os.path.exists(conf_path):
            QMessageBox.warning(self, "DNS патч", f"Файл не найден:\n{conf_path}")
            return

        changed = comment_dns_in_config(conf_path)
        if changed:
            QMessageBox.information(
                self, "DNS патч",
                f"Строки DNS= закомментированы в:\n{conf_path}\n\n"
                "Переподключитесь, чтобы изменения вступили в силу."
            )
        else:
            QMessageBox.information(
                self, "DNS патч",
                "Строк DNS= не найдено (уже закомментированы или их нет)."
            )

    def is_autostart_enabled(self) -> bool:
        return os.path.exists(AUTOSTART_FILE)

    def refresh_autostart_btn(self):
        if self.is_autostart_enabled():
            self.btn_autostart.setText("✅ УБРАТЬ ИЗ АВТОЗАГРУЗКИ")
            self.btn_autostart.setStyleSheet("background-color: #3b2f2f; color: #f7768e;")
        else:
            self.btn_autostart.setText("🔁 ДОБАВИТЬ В АВТОЗАГРУЗКУ")
            self.btn_autostart.setStyleSheet("background-color: #1f4b3a; color: #9ece6a;")

    def toggle_autostart(self):
        if self.is_autostart_enabled():
            try:
                os.remove(AUTOSTART_FILE)
                QMessageBox.information(self, "Автозагрузка", "Убрано из автозагрузки.")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e))
        else:
            os.makedirs(AUTOSTART_DIR, exist_ok=True)
            desktop = (
                "[Desktop Entry]\n"
                "Type=Application\n"
                "Name=Mini VPN\n"
                "Comment=WireGuard VPN Manager\n"
                f"Exec=python3 {SCRIPT_PATH}\n"
                "Icon=network-vpn\n"
                "Terminal=false\n"
                "X-GNOME-Autostart-enabled=true\n"
            )
            try:
                with open(AUTOSTART_FILE, 'w') as f:
                    f.write(desktop)
                QMessageBox.information(
                    self, "Автозагрузка",
                    f"Добавлено в автозагрузку.\nФайл: {AUTOSTART_FILE}"
                )
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e))

        self.refresh_autostart_btn()

    def handle_info_update(self, ip, ping):
        self.current_ip = ip
        self.ping_label.setText(f"Ping: {ping} ms")
        self.update_ip_text()

    def toggle_ip_visibility(self):
        self.ip_hidden = not self.ip_hidden
        self.update_ip_text()

    def update_ip_text(self):
        if self.ip_hidden:
            self.ip_display.setText("ВАШ IP: ••••••••••••••")
        else:
            self.ip_display.setText(f"ВАШ IP: {self.current_ip}")

    def refresh_configs(self):
        try:
            files = [f.replace('.conf', '') for f in os.listdir(CONFIG_DIR) if f.endswith('.conf')]
            self.combo.clear()
            self.combo.addItems(sorted(files) if files else ["Пусто"])
        except:
            pass

    def rename_config(self):
        old = self.combo.currentText()
        if not old or "Пусто" in old:
            return
        new, ok = QInputDialog.getText(self, 'Переименование', f'Новое имя для «{old}»:')
        if ok and new:
            try:
                os.rename(
                    os.path.join(CONFIG_DIR, f"{old}.conf"),
                    os.path.join(CONFIG_DIR, f"{new}.conf")
                )
                self.refresh_configs()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e))

    def update_status(self):
        try:
            with open("/proc/net/dev", "r") as f:
                content = f.read()
            active = next(
                (self.combo.itemText(i) for i in range(self.combo.count())
                 if self.combo.itemText(i) in content),
                None
            )
            if active:
                self.status_card.setText(f"АКТИВЕН: {active.upper()}")
                self.status_card.setStyleSheet(
                    "background-color: #9ece6a; color: #1a1b26; "
                    "border-radius: 10px; font-weight: bold; padding: 12px;"
                )
            else:
                self.status_card.setText("VPN ВЫКЛЮЧЕН")
                self.status_card.setStyleSheet(
                    "background-color: #414868; color: #a9b1d6; "
                    "border-radius: 10px; padding: 12px;"
                )
        except:
            pass

    def connect_vpn(self):
        selected = self.combo.currentText()
        if selected and "Пусто" not in selected:
            path = os.path.join(CONFIG_DIR, f"{selected}.conf")
            result = subprocess.run(['sudo', 'wg-quick', 'up', path], capture_output=True, text=True)
            if result.returncode != 0:
                QMessageBox.warning(self, "Ошибка подключения", result.stderr or "Неизвестная ошибка")

    def disconnect_all(self):
        selected = self.combo.currentText()
        if selected and "Пусто" not in selected:
            path = os.path.join(CONFIG_DIR, f"{selected}.conf")
            subprocess.run(['sudo', 'wg-quick', 'down', path], capture_output=True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    check_first_run(app)
    window = UltimateVPN()
    window.show()
    sys.exit(app.exec())
