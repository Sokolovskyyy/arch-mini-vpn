#!/usr/bin/python3
import sys
import subprocess
import os
import re
import json
import shutil
import requests
import time
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QLabel, QComboBox, QHBoxLayout, QInputDialog,
                             QMessageBox, QDialog, QCheckBox, QSizePolicy)
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal, QSize

CONFIG_DIR     = os.path.expanduser("~/vpn-configs")
APP_DIR        = os.path.expanduser("~/.config/mini-vpn")
FIRST_RUN_FLAG = os.path.join(APP_DIR, ".first_run_done")
SETTINGS_FILE  = os.path.join(APP_DIR, "settings.json")
AUTOSTART_DIR  = os.path.expanduser("~/.config/autostart")
AUTOSTART_FILE = os.path.join(AUTOSTART_DIR, "mini-vpn.desktop")
SCRIPT_PATH    = os.path.abspath(__file__)

WIN_MIN_W, WIN_MIN_H = 340, 348
WIN_DEF_W, WIN_DEF_H = 400, 330

GITHUB_URL = "https://github.com/Sokolovskyyy/arch-mini-vpn"

THEME_KEYS = ["tokyo", "white", "blue", "amoled", "violet", "pink", "system"]

THEME_STYLES = {
    "tokyo": {
        "bg":           "#1a1b26",
        "fg":           "#a9b1d6",
        "card_idle":    "#414868",
        "card_idle_fg": "#a9b1d6",
        "btn_bg":       "#444b6a",
        "btn_hover":    "#565f89",
        "combo_bg":     "#24283b",
        "combo_brd":    "#414868",
        "ip_col":       "#7aa2f7",
        "ping_col":     "#bb9af7",
        "gear_bg":      "#2a2d3e",
        "gear_hover":   "#414868",
        "dns_bg":       "#2d4f67",
        "dns_fg":       "#7dcfff",
        "conn_bg":      "#7dbe50",
        "conn_fg":      "#1a1b26",
        "disc_bg":      "#c9556a",
        "disc_fg":      "#1a1b26",
    },
    "white": {
        "bg":           "#f4f5f7",
        "fg":           "#2c2e3a",
        "card_idle":    "#dde1ec",
        "card_idle_fg": "#4a4f6a",
        "btn_bg":       "#d0d4e8",
        "btn_hover":    "#b8bdd6",
        "combo_bg":     "#ffffff",
        "combo_brd":    "#c5c9dc",
        "ip_col":       "#3b6cd4",
        "ping_col":     "#7b52c2",
        "gear_bg":      "#e2e5f0",
        "gear_hover":   "#c8ccde",
        "dns_bg":       "#c2d8ef",
        "dns_fg":       "#1a4f7a",
        "conn_bg":      "#4a9e4a",
        "conn_fg":      "#ffffff",
        "disc_bg":      "#b84040",
        "disc_fg":      "#ffffff",
    },
    "blue": {
        "bg":           "#0d1b2a",
        "fg":           "#a8c8e8",
        "card_idle":    "#1b3a5c",
        "card_idle_fg": "#7ab3d4",
        "btn_bg":       "#1e4d78",
        "btn_hover":    "#2a6399",
        "combo_bg":     "#122840",
        "combo_brd":    "#1e4d78",
        "ip_col":       "#5bc8fa",
        "ping_col":     "#8adcff",
        "gear_bg":      "#142035",
        "gear_hover":   "#1e4060",
        "dns_bg":       "#0e3256",
        "dns_fg":       "#5bc8fa",
        "conn_bg":      "#1e7a50",
        "conn_fg":      "#d0fff0",
        "disc_bg":      "#8a2535",
        "disc_fg":      "#ffd8dc",
    },
    "amoled": {
        "bg":           "#000000",
        "fg":           "#cccccc",
        "card_idle":    "#111111",
        "card_idle_fg": "#888888",
        "btn_bg":       "#1a1a1a",
        "btn_hover":    "#2a2a2a",
        "combo_bg":     "#0d0d0d",
        "combo_brd":    "#2a2a2a",
        "ip_col":       "#00e5ff",
        "ping_col":     "#b388ff",
        "gear_bg":      "#0d0d0d",
        "gear_hover":   "#1f1f1f",
        "dns_bg":       "#0a1a1a",
        "dns_fg":       "#00e5ff",
        "conn_bg":      "#1a8040",
        "conn_fg":      "#ccffdd",
        "disc_bg":      "#a02020",
        "disc_fg":      "#ffe0e0",
    },
    "violet": {
        "bg":           "#12052a",
        "fg":           "#e8d8ff",
        "card_idle":    "#261050",
        "card_idle_fg": "#c4b5fd",
        "btn_bg":       "#3b1878",
        "btn_hover":    "#5b28b4",
        "combo_bg":     "#1a0840",
        "combo_brd":    "#6d28d9",
        "ip_col":       "#c084fc",
        "ping_col":     "#a78bfa",
        "gear_bg":      "#1a0840",
        "gear_hover":   "#3b1878",
        "dns_bg":       "#1e0a46",
        "dns_fg":       "#c084fc",
        "conn_bg":      "#7c3aed",
        "conn_fg":      "#faf5ff",
        "disc_bg":      "#be185d",
        "disc_fg":      "#fff0f7",
    },
    "pink": {
        "bg":           "#fff0f5",
        "fg":           "#5a3a4a",
        "card_idle":    "#f8d7e3",
        "card_idle_fg": "#7a4060",
        "btn_bg":       "#f0b8cc",
        "btn_hover":    "#e896b0",
        "combo_bg":     "#fff5f8",
        "combo_brd":    "#f0b8cc",
        "ip_col":       "#c2185b",
        "ping_col":     "#ad1457",
        "gear_bg":      "#fce4ec",
        "gear_hover":   "#f8bbd0",
        "dns_bg":       "#fce4ec",
        "dns_fg":       "#880e4f",
        "conn_bg":      "#c0547a",
        "conn_fg":      "#ffffff",
        "disc_bg":      "#8f3030",
        "disc_fg":      "#ffe8e8",
    },
    "system": None,
}

def get_theme_qss(key: str) -> str:
    if key == "system" or key not in THEME_STYLES:
        return ""
    c = THEME_STYLES[key]
    return f"""
        QWidget {{
            background-color: {c['bg']};
            color: {c['fg']};
            font-family: 'Cantarell', sans-serif;
        }}
        QPushButton {{
            border-radius: 6px; padding: 10px;
            font-weight: bold;
            background-color: {c['btn_bg']}; color: {c['fg']};
        }}
        QPushButton:hover {{ background-color: {c['btn_hover']}; }}
        QComboBox {{
            background-color: {c['combo_bg']};
            border: 1px solid {c['combo_brd']};
            padding: 5px; color: {c['fg']};
        }}
        QDialog {{
            background-color: {c['bg']}; color: {c['fg']};
        }}
        QLabel {{ color: {c['fg']}; }}
        QCheckBox {{ color: {c['fg']}; spacing: 8px; }}
        QCheckBox::indicator {{
            width: 16px; height: 16px; border-radius: 4px;
            border: 2px solid {c['combo_brd']}; background: {c['combo_bg']};
        }}
        QCheckBox::indicator:checked {{
            background: {c['ip_col']}; border-color: {c['ip_col']};
        }}
    """

def apply_theme_to_window(window, key: str):
    window.setStyleSheet(get_theme_qss(key))
    if key == "system":
        window.ip_display.setStyleSheet("")
        window.ping_label.setStyleSheet("")
        window.btn_settings.setStyleSheet("")
        window.btn_dns.setStyleSheet("")
        window.btn_up.setStyleSheet("")
        window.btn_down.setStyleSheet("")
        window.status_card.setStyleSheet(
            "#statusCard { border-radius: 10px; font-weight: bold; padding: 12px;"
            " border: 2px solid palette(mid);"
            " background-color: palette(button); color: palette(buttonText); }")
        return

    c = THEME_STYLES[key]
    window.ip_display.setStyleSheet(
        f"color: {c['ip_col']}; font-size: 14px; font-weight: bold;"
        " border: none; background: transparent; padding: 5px;")
    window.ping_label.setStyleSheet(f"color: {c['ping_col']};")
    window.btn_settings.setStyleSheet(
        f"QPushButton {{ background-color: {c['gear_bg']}; color: {c['fg']};"
        " border-radius: 10px; font-size: 20px; padding: 0px; font-weight: normal; }"
        f"QPushButton:hover {{ background-color: {c['gear_hover']}; }}")
    window.btn_dns.setStyleSheet(
        f"background-color: {c['dns_bg']}; color: {c['dns_fg']};")
    window.btn_up.setStyleSheet(
        f"background-color: {c['conn_bg']}; color: {c['conn_fg']};"
        " font-size: 14px;")
    window.btn_down.setStyleSheet(
        f"background-color: {c['disc_bg']}; color: {c['disc_fg']};")

def status_style_active(key: str) -> str:
    if key == "system":
        return ("#statusCard { border-radius: 10px; font-weight: bold; padding: 12px;"
                " border: 2px solid palette(mid);"
                " background-color: palette(button); color: palette(buttonText); }")
    c = THEME_STYLES.get(key, THEME_STYLES["tokyo"])
    return (f"#statusCard {{ background-color: {c['conn_bg']}; color: {c['conn_fg']};"
            f" border: 2px solid {c['fg']};"
            " border-radius: 10px; font-weight: bold; padding: 12px; }}")

def status_style_idle(key: str) -> str:
    if key == "system":
        return ("#statusCard { border-radius: 10px; padding: 12px;"
                " border: 2px solid palette(mid);"
                " background-color: palette(button); color: palette(buttonText); }")
    c = THEME_STYLES.get(key, THEME_STYLES["tokyo"])
    return (f"#statusCard {{ background-color: {c['card_idle']}; color: {c['card_idle_fg']};"
            f" border: 2px solid {c['fg']};"
            " border-radius: 10px; padding: 12px; }}")

DISTROS = {
    "arch": {
        "label":   "Arch / Manjaro / EndeavourOS",
        "pm":      "pacman",
        "install": "sudo pacman -S --needed --noconfirm {pkgs}",
        "term":    ["konsole", "kitty", "alacritty", "gnome-terminal", "xterm"],
        "pkgs": {
            "wireguard-tools": "wireguard-tools",
            "openresolv":      "openresolv",
            "python-requests": "python-requests",
        },
        "binaries": ["wg", "wg-quick"],
    },
    "debian": {
        "label":   "Debian / Ubuntu / Mint / Pop!_OS",
        "pm":      "apt",
        "install": "sudo apt-get install -y {pkgs}",
        "term":    ["gnome-terminal", "konsole", "kitty", "alacritty", "xterm"],
        "pkgs": {
            "wireguard-tools": "wireguard",
            "openresolv":      "openresolv",
            "python-requests": "python3-requests",
        },
        "binaries": ["wg", "wg-quick"],
    },
    "fedora": {
        "label":   "Fedora / RHEL / CentOS",
        "pm":      "dnf",
        "install": "sudo dnf install -y {pkgs}",
        "term":    ["gnome-terminal", "konsole", "kitty", "xterm"],
        "pkgs": {
            "wireguard-tools": "wireguard-tools",
            "openresolv":      "openresolv",
            "python-requests": "python3-requests",
        },
        "binaries": ["wg", "wg-quick"],
    },
    "opensuse": {
        "label":   "openSUSE Tumbleweed / Leap",
        "pm":      "zypper",
        "install": "sudo zypper install -y {pkgs}",
        "term":    ["konsole", "gnome-terminal", "xterm"],
        "pkgs": {
            "wireguard-tools": "wireguard-tools",
            "openresolv":      "openresolv",
            "python-requests": "python3-requests",
        },
        "binaries": ["wg", "wg-quick"],
    },
    "void": {
        "label":   "Void Linux",
        "pm":      "xbps",
        "install": "sudo xbps-install -Sy {pkgs}",
        "term":    ["xterm", "kitty", "alacritty"],
        "pkgs": {
            "wireguard-tools": "wireguard-tools",
            "openresolv":      "openresolv",
            "python-requests": "python3-requests",
        },
        "binaries": ["wg", "wg-quick"],
    },
}

def detect_distro() -> str:
    try:
        with open("/etc/os-release") as f:
            c = f.read().lower()
    except:
        return "unknown"
    if any(x in c for x in ["arch", "manjaro", "endeavouros", "garuda", "artix"]):
        return "arch"
    if any(x in c for x in ["debian", "ubuntu", "mint", "pop", "elementary", "kali", "zorin"]):
        return "debian"
    if any(x in c for x in ["fedora", "rhel", "centos", "rocky", "alma"]):
        return "fedora"
    if any(x in c for x in ["opensuse", "suse"]):
        return "opensuse"
    if "void" in c:
        return "void"
    return "unknown"

def find_terminal(distro_key: str) -> list:
    candidates = (DISTROS.get(distro_key, {}).get("term", []) +
                  ["gnome-terminal", "konsole", "kitty", "alacritty",
                   "xfce4-terminal", "xterm"])
    for term in candidates:
        if shutil.which(term):
            return [term, "--"] if term == "gnome-terminal" else [term, "-e"]
    return ["xterm", "-e"]

def build_install_cmd(distro_key: str, pkg_keys: list) -> str:
    distro = DISTROS.get(distro_key)
    if not distro:
        return ""
    names = [n for k in pkg_keys if (n := distro["pkgs"].get(k, k))]
    return distro["install"].format(pkgs=" ".join(names)) if names else ""

def run_in_terminal(distro_key: str, cmd: str, title: str = "Mini VPN"):
    term, flag = find_terminal(distro_key)[:1][0], find_terminal(distro_key)[1]
    shell = f"echo '>>> {title}'; echo; {cmd}; echo; echo '✓ Done! Closing in 3s...'; sleep 3"
    if term == "gnome-terminal":
        subprocess.Popen([term, "--", "sh", "-c", shell])
    else:
        subprocess.run([term, flag, "sh", "-c", shell])

def check_dependencies(distro_key: str) -> list:
    if distro_key == "unknown":
        return []
    return [b for b in DISTROS[distro_key]["binaries"] if not shutil.which(b)]

TRANSLATIONS = {
    "ru": {
        "window_title":        "Mini VPN",
        "status_ready":        "СИСТЕМА ГОТОВА",
        "status_active":       "АКТИВЕН: {}",
        "status_off":          "VPN ВЫКЛЮЧЕН",
        "ip_hidden":           "ВАШ IP: ••••••••••••••",
        "ip_shown":            "ВАШ IP: {}",
        "ping":                "Ping: {} ms",
        "select_server":       "Выберите сервер:",
        "empty":               "Пусто",
        "btn_dns":             "🔇 ЗАКОММЕНТИРОВАТЬ DNS В КОНФИГЕ",
        "btn_connect":         "⚡ ВКЛЮЧИТЬ VPN",
        "btn_disconnect":      "🛑 ВЫКЛЮЧИТЬ VPN",
        "rename_title":        "Переименование",
        "rename_prompt":       "Новое имя для «{}»:",
        "dns_no_config":       "Сначала выберите конфиг.",
        "dns_not_found":       "Файл не найден:\n{}",
        "dns_patched":         "Строки DNS= закомментированы в:\n{}\n\nПереподключитесь для применения.",
        "dns_already":         "Строк DNS= не найдено (уже закомментированы или их нет).",
        "dns_title":           "DNS патч",
        "error_title":         "Ошибка",
        "conn_error":          "Ошибка подключения",
        "settings_title":      "Настройки",
        "settings_autostart":  "Запускать при входе в систему",
        "settings_lang":       "Язык / Language",
        "settings_theme":      "Тема оформления",
        "settings_close":      "Закрыть",
        "settings_github":     "GitHub репозиторий",
        "theme_tokyo":         "Tokyo Night",
        "theme_white":         "Светлая",
        "theme_blue":          "Синяя",
        "theme_amoled":        "AMOLED",
        "theme_violet":        "Фиолетовая",
        "theme_pink":          "Мягкий розовый",
        "theme_system":        "Системная",
        "first_distro":        "Определён дистрибутив: <b>{}</b>",
        "first_unknown":       "Дистрибутив не распознан.\nУстанови вручную: wireguard-tools, openresolv",
        "first_question":      "Установить все необходимые пакеты?<br><br><code>{}</code><br><br>Потребуется пароль sudo.",
        "first_skip":          "Пропустить",
        "deps_missing_title":  "Отсутствуют зависимости",
        "deps_missing_text":   "Не найдены команды: <b>{}</b><br><br>Установить сейчас?",
    },
    "en": {
        "window_title":        "Mini VPN",
        "status_ready":        "SYSTEM READY",
        "status_active":       "ACTIVE: {}",
        "status_off":          "VPN OFF",
        "ip_hidden":           "YOUR IP: ••••••••••••••",
        "ip_shown":            "YOUR IP: {}",
        "ping":                "Ping: {} ms",
        "select_server":       "Select server:",
        "empty":               "Empty",
        "btn_dns":             "🔇 COMMENT OUT DNS IN CONFIG",
        "btn_connect":         "⚡ CONNECT VPN",
        "btn_disconnect":      "🛑 DISCONNECT VPN",
        "rename_title":        "Rename",
        "rename_prompt":       "New name for «{}»:",
        "dns_no_config":       "Please select a config first.",
        "dns_not_found":       "File not found:\n{}",
        "dns_patched":         "DNS= lines commented out in:\n{}\n\nReconnect to apply.",
        "dns_already":         "No DNS= lines found (already commented or absent).",
        "dns_title":           "DNS Patch",
        "error_title":         "Error",
        "conn_error":          "Connection error",
        "settings_title":      "Settings",
        "settings_autostart":  "Launch at login",
        "settings_lang":       "Language / Язык",
        "settings_theme":      "Color theme",
        "settings_close":      "Close",
        "settings_github":     "GitHub repository",
        "theme_tokyo":         "Tokyo Night",
        "theme_white":         "Light",
        "theme_blue":          "Blue",
        "theme_amoled":        "AMOLED",
        "theme_violet":        "Violet",
        "theme_pink":          "Soft Pink",
        "theme_system":        "System",
        "first_distro":        "Detected: <b>{}</b>",
        "first_unknown":       "Distro not recognised.\nInstall manually: wireguard-tools, openresolv",
        "first_question":      "Install all required packages?<br><br><code>{}</code><br><br>sudo password required.",
        "first_skip":          "Skip",
        "deps_missing_title":  "Missing dependencies",
        "deps_missing_text":   "Commands not found: <b>{}</b><br><br>Install now?",
    },
}

def load_settings() -> dict:
    os.makedirs(APP_DIR, exist_ok=True)
    try:
        with open(SETTINGS_FILE) as f:
            return json.load(f)
    except:
        return {"lang": "ru", "theme": "tokyo",
                "win_w": WIN_DEF_W, "win_h": WIN_DEF_H}

def save_settings(data: dict):
    os.makedirs(APP_DIR, exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f)

def handle_first_run(t: dict, distro_key: str):
    if os.path.exists(FIRST_RUN_FLAG):
        return
    os.makedirs(APP_DIR, exist_ok=True)
    if distro_key == "unknown":
        QMessageBox.warning(None, t["first_title"], t["first_unknown"])
    else:
        cmd = build_install_cmd(distro_key, ["wireguard-tools", "openresolv", "python-requests"])
        msg = QMessageBox()
        msg.setWindowTitle(t["first_title"])
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText(t["first_distro"].format(DISTROS[distro_key]["label"]) +
                    "<br><br>" + t["first_question"].format(cmd))
        btn_yes  = msg.addButton(QMessageBox.StandardButton.Yes)
        msg.addButton(t["first_skip"], QMessageBox.ButtonRole.RejectRole)
        msg.setDefaultButton(btn_yes)
        msg.exec()
        if msg.clickedButton() == btn_yes:
            run_in_terminal(distro_key, cmd, t["first_title"])
    with open(FIRST_RUN_FLAG, "w") as f:
        f.write("done\n")

def handle_deps_check(t: dict, distro_key: str):
    missing = check_dependencies(distro_key)
    if not missing:
        return
    msg = QMessageBox()
    msg.setWindowTitle(t["deps_missing_title"])
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setText(t["deps_missing_text"].format(", ".join(missing)))
    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    if msg.exec() == QMessageBox.StandardButton.Yes:
        pkg_keys = []
        if any(b in missing for b in ["wg", "wg-quick"]):
            pkg_keys.append("wireguard-tools")
        if "resolvconf" in missing:
            pkg_keys.append("openresolv")
        cmd = build_install_cmd(distro_key, pkg_keys)
        if cmd:
            run_in_terminal(distro_key, cmd, t["deps_missing_title"])

def comment_dns_in_config(conf_path: str) -> bool:
    try:
        with open(conf_path) as f:
            lines = f.readlines()
        new_lines, changed = [], False
        for line in lines:
            if re.match(r"^\s*DNS\s*=", line, re.IGNORECASE):
                new_lines.append("# " + line)
                changed = True
            else:
                new_lines.append(line)
        if changed:
            with open(conf_path, "w") as f:
                f.writelines(new_lines)
        return changed
    except Exception as e:
        print(f"[DNS] {e}")
        return False

class MonitorThread(QThread):
    info_updated = pyqtSignal(str, str)

    def run(self):
        while True:
            ip, ping = "—", "—"
            try:
                r = requests.get("https://api.ipify.org", timeout=3)
                if r.status_code == 200:
                    ip = r.text.strip()
                p = subprocess.run(["ping", "-c", "1", "-W", "1", "1.1.1.1"],
                                   capture_output=True, text=True)
                if p.returncode == 0:
                    ping = p.stdout.split("time=")[1].split(" ms")[0]
            except:
                pass
            self.info_updated.emit(ip, ping)
            time.sleep(7)

class SettingsDialog(QDialog):
    lang_changed  = pyqtSignal(str)
    theme_changed = pyqtSignal(str)

    def __init__(self, parent, t: dict, settings: dict):
        super().__init__(parent)
        self.t        = t
        self.settings = settings
        self.setWindowTitle(t["settings_title"])
        self.setFixedSize(340, 260)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        self.chk_autostart = QCheckBox(t["settings_autostart"])
        self.chk_autostart.setChecked(os.path.exists(AUTOSTART_FILE))
        self.chk_autostart.toggled.connect(self._toggle_autostart)
        layout.addWidget(self.chk_autostart)

        lang_row = QHBoxLayout()
        self.lbl_lang = QLabel(t["settings_lang"])
        lang_row.addWidget(self.lbl_lang)
        lang_row.addStretch()
        self.btn_lang = QPushButton()
        self.btn_lang.setFixedWidth(74)
        self._refresh_lang_btn()
        self.btn_lang.clicked.connect(self._switch_lang)
        lang_row.addWidget(self.btn_lang)
        layout.addLayout(lang_row)

        theme_row = QHBoxLayout()
        self.lbl_theme = QLabel(t["settings_theme"])
        theme_row.addWidget(self.lbl_theme)
        theme_row.addStretch()
        self.combo_theme = QComboBox()
        self.combo_theme.setFixedWidth(175)
        self._fill_theme_combo()
        self.combo_theme.currentIndexChanged.connect(self._change_theme)
        theme_row.addWidget(self.combo_theme)
        layout.addLayout(theme_row)

        layout.addStretch()

        self.btn_github = QPushButton(f"🔗  {t['settings_github']}")
        self.btn_github.clicked.connect(
            lambda: subprocess.run(["xdg-open", GITHUB_URL]))
        layout.addWidget(self.btn_github)

        self.btn_close = QPushButton(t["settings_close"])
        self.btn_close.clicked.connect(self.accept)
        layout.addWidget(self.btn_close)

        self.setLayout(layout)
        self._sync_theme()

    def _fill_theme_combo(self):
        cur_theme = self.settings.get("theme", "tokyo")
        self.combo_theme.blockSignals(True)
        self.combo_theme.clear()
        for key in THEME_KEYS:
            label = self.t.get(f"theme_{key}", key)
            self.combo_theme.addItem(label, key)
        idx = THEME_KEYS.index(cur_theme) if cur_theme in THEME_KEYS else 0
        self.combo_theme.setCurrentIndex(idx)
        self.combo_theme.blockSignals(False)

    def _sync_theme(self):
        key = self.settings.get("theme", "tokyo")
        self.setStyleSheet(get_theme_qss(key))

    def _refresh_lang_btn(self):
        self.btn_lang.setText(
            "🇷🇺 RU" if self.settings.get("lang", "ru") == "ru" else "🇬🇧 EN")

    def _switch_lang(self):
        new = "en" if self.settings.get("lang", "ru") == "ru" else "ru"
        self.settings["lang"] = new
        save_settings(self.settings)
        self._refresh_lang_btn()
        self.t = TRANSLATIONS[new]
        self.setWindowTitle(self.t["settings_title"])
        self.chk_autostart.setText(self.t["settings_autostart"])
        self.lbl_lang.setText(self.t["settings_lang"])
        self.lbl_theme.setText(self.t["settings_theme"])
        self.btn_github.setText(f"🔗  {self.t['settings_github']}")
        self.btn_close.setText(self.t["settings_close"])
        self._fill_theme_combo()
        self.lang_changed.emit(new)

    def _change_theme(self, idx: int):
        key = self.combo_theme.itemData(idx)
        if not key:
            return
        self.settings["theme"] = key
        save_settings(self.settings)
        self._sync_theme()
        self.theme_changed.emit(key)

    def _toggle_autostart(self, checked: bool):
        if checked:
            os.makedirs(AUTOSTART_DIR, exist_ok=True)
            try:
                with open(AUTOSTART_FILE, "w") as f:
                    f.write(
                        "[Desktop Entry]\nType=Application\nName=Mini VPN\n"
                        "Comment=WireGuard VPN Manager\n"
                        f"Exec=python3 {SCRIPT_PATH}\n"
                        "Icon=network-vpn\nTerminal=false\n"
                        "X-GNOME-Autostart-enabled=true\n"
                    )
            except Exception as e:
                QMessageBox.warning(self, self.t["error_title"], str(e))
                self.chk_autostart.blockSignals(True)
                self.chk_autostart.setChecked(False)
                self.chk_autostart.blockSignals(False)
        else:
            try:
                if os.path.exists(AUTOSTART_FILE):
                    os.remove(AUTOSTART_FILE)
            except Exception as e:
                QMessageBox.warning(self, self.t["error_title"], str(e))

class UltimateVPN(QWidget):
    def __init__(self, distro_key: str):
        super().__init__()
        self.distro_key = distro_key
        self.current_ip = "..."
        self.ip_hidden  = True
        self.settings   = load_settings()
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._save_window_size)

        os.makedirs(CONFIG_DIR, exist_ok=True)
        self._build_ui()
        self._restore_size()
        self._apply_theme(self.settings.get("theme", "tokyo"))

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1500)

        self.monitor = MonitorThread()
        self.monitor.info_updated.connect(self._on_monitor)
        self.monitor.start()

    @property
    def t(self) -> dict:
        return TRANSLATIONS[self.settings.get("lang", "ru")]

    def _restore_size(self):
        w = max(self.settings.get("win_w", WIN_DEF_W), WIN_MIN_W)
        h = max(self.settings.get("win_h", WIN_DEF_H), WIN_MIN_H)
        self.resize(w, h)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._resize_timer.start(500)

    def _save_window_size(self):
        self.settings["win_w"] = self.width()
        self.settings["win_h"] = self.height()
        save_settings(self.settings)

    def _apply_theme(self, key: str):
        apply_theme_to_window(self, key)
        self.update_status()

    def _build_ui(self):
        self.setWindowTitle(self.t["window_title"])
        self.setMinimumSize(WIN_MIN_W, WIN_MIN_H)

        layout = QVBoxLayout()
        layout.setSpacing(6)

        status_row = QHBoxLayout()
        status_row.setSpacing(6)

        self.status_card = QLabel(self.t["status_ready"])
        self.status_card.setObjectName("statusCard")
        self.status_card.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_card.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        status_row.addWidget(self.status_card, 1)

        self.btn_settings = QPushButton("⚙")
        self.btn_settings.setFixedSize(44, 44)
        self.btn_settings.setToolTip("Settings / Настройки")
        self.btn_settings.clicked.connect(self._open_settings)
        status_row.addWidget(self.btn_settings)
        layout.addLayout(status_row)

        self.ip_display = QPushButton(self.t["ip_hidden"])
        self.ip_display.setFlat(True)
        self.ip_display.clicked.connect(self._toggle_ip)
        layout.addWidget(self.ip_display)

        self.ping_label = QLabel(self.t["ping"].format("---"))
        self.ping_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.ping_label)

        self.lbl_server = QLabel(self.t["select_server"])
        layout.addWidget(self.lbl_server)

        cfg_row = QHBoxLayout()
        self.combo = QComboBox()
        self.combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._refresh_configs()
        cfg_row.addWidget(self.combo, 1)

        btn_rename = QPushButton("📝")
        btn_rename.setFixedWidth(40)
        btn_rename.setToolTip("Rename")
        btn_rename.clicked.connect(self._rename_config)
        cfg_row.addWidget(btn_rename)

        btn_open = QPushButton("📂")
        btn_open.setFixedWidth(40)
        btn_open.setToolTip("Open folder")
        btn_open.clicked.connect(lambda: subprocess.run(["xdg-open", CONFIG_DIR]))
        cfg_row.addWidget(btn_open)
        layout.addLayout(cfg_row)

        layout.addStretch()

        self.btn_dns = QPushButton(self.t["btn_dns"])
        self.btn_dns.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_dns.clicked.connect(self._patch_dns)
        layout.addWidget(self.btn_dns)

        self.btn_up = QPushButton(self.t["btn_connect"])
        self.btn_up.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.btn_up.setMinimumHeight(50)
        self.btn_up.clicked.connect(self._connect)
        layout.addWidget(self.btn_up)

        self.btn_down = QPushButton(self.t["btn_disconnect"])
        self.btn_down.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_down.setMinimumHeight(40)
        self.btn_down.clicked.connect(self._disconnect)
        layout.addWidget(self.btn_down)

        self.setLayout(layout)

    def _open_settings(self):
        dlg = SettingsDialog(self, self.t, self.settings)
        dlg.lang_changed.connect(self._apply_lang)
        dlg.theme_changed.connect(self._apply_theme)
        dlg.exec()

    def _apply_lang(self, lang: str):
        self.settings["lang"] = lang
        t = self.t
        self.setWindowTitle(t["window_title"])
        self.lbl_server.setText(t["select_server"])
        self.btn_dns.setText(t["btn_dns"])
        self.btn_up.setText(t["btn_connect"])
        self.btn_down.setText(t["btn_disconnect"])
        self.ping_label.setText(t["ping"].format("---"))
        self._update_ip_label()
        self.update_status()
        if self.combo.count() == 1 and self.combo.itemText(0) in ("Пусто", "Empty"):
            self.combo.setItemText(0, t["empty"])

    def _on_monitor(self, ip, ping):
        self.current_ip = ip
        self.ping_label.setText(self.t["ping"].format(ping))
        self._update_ip_label()

    def _toggle_ip(self):
        self.ip_hidden = not self.ip_hidden
        self._update_ip_label()

    def _update_ip_label(self):
        self.ip_display.setText(
            self.t["ip_hidden"] if self.ip_hidden
            else self.t["ip_shown"].format(self.current_ip))

    def _refresh_configs(self):
        try:
            files = [f[:-5] for f in os.listdir(CONFIG_DIR) if f.endswith(".conf")]
            self.combo.clear()
            self.combo.addItems(sorted(files) if files else [self.t["empty"]])
        except:
            pass

    def _rename_config(self):
        old = self.combo.currentText()
        if not old or old == self.t["empty"]:
            return
        new, ok = QInputDialog.getText(
            self, self.t["rename_title"], self.t["rename_prompt"].format(old))
        if ok and new:
            try:
                os.rename(os.path.join(CONFIG_DIR, f"{old}.conf"),
                          os.path.join(CONFIG_DIR, f"{new}.conf"))
                self._refresh_configs()
            except Exception as e:
                QMessageBox.warning(self, self.t["error_title"], str(e))

    def update_status(self):
        theme = self.settings.get("theme", "tokyo")
        try:
            with open("/proc/net/dev") as f:
                content = f.read()
            active = next(
                (self.combo.itemText(i) for i in range(self.combo.count())
                 if self.combo.itemText(i) in content), None)
            if active:
                self.status_card.setText(self.t["status_active"].format(active.upper()))
                self.status_card.setStyleSheet(status_style_active(theme))
            else:
                self.status_card.setText(self.t["status_off"])
                self.status_card.setStyleSheet(status_style_idle(theme))
        except:
            self.status_card.setText(self.t["status_ready"])
            self.status_card.setStyleSheet(status_style_idle(theme))

    def _patch_dns(self):
        sel = self.combo.currentText()
        if not sel or sel == self.t["empty"]:
            QMessageBox.warning(self, self.t["dns_title"], self.t["dns_no_config"])
            return
        path = os.path.join(CONFIG_DIR, f"{sel}.conf")
        if not os.path.exists(path):
            QMessageBox.warning(self, self.t["dns_title"],
                                self.t["dns_not_found"].format(path))
            return
        if comment_dns_in_config(path):
            QMessageBox.information(self, self.t["dns_title"],
                                    self.t["dns_patched"].format(path))
        else:
            QMessageBox.information(self, self.t["dns_title"], self.t["dns_already"])

    def _connect(self):
        sel = self.combo.currentText()
        if sel and sel != self.t["empty"]:
            r = subprocess.run(["sudo", "wg-quick", "up",
                                os.path.join(CONFIG_DIR, f"{sel}.conf")],
                               capture_output=True, text=True)
            if r.returncode != 0:
                QMessageBox.warning(self, self.t["conn_error"], r.stderr or "Unknown error")

    def _disconnect(self):
        sel = self.combo.currentText()
        if sel and sel != self.t["empty"]:
            subprocess.run(["sudo", "wg-quick", "down",
                            os.path.join(CONFIG_DIR, f"{sel}.conf")],
                           capture_output=True)

if __name__ == "__main__":
    app        = QApplication(sys.argv)
    settings   = load_settings()
    t          = TRANSLATIONS[settings.get("lang", "ru")]
    distro_key = detect_distro()

    handle_first_run(t, distro_key)
    handle_deps_check(t, distro_key)

    window = UltimateVPN(distro_key)
    window.show()
    sys.exit(app.exec())
