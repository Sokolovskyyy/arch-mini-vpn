<div align="center">

```
 ███╗   ███╗██╗███╗   ██╗██╗    ██╗   ██╗██████╗ ███╗   ██╗
 ████╗ ████║██║████╗  ██║██║    ██║   ██║██╔══██╗████╗  ██║
 ██╔████╔██║██║██╔██╗ ██║██║    ██║   ██║██████╔╝██╔██╗ ██║
 ██║╚██╔╝██║██║██║╚██╗██║██║    ╚██╗ ██╔╝██╔═══╝ ██║╚██╗██║
 ██║ ╚═╝ ██║██║██║ ╚████║██║     ╚████╔╝ ██║     ██║ ╚████║
 ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝     ╚═══╝  ╚═╝     ╚═╝  ╚═══╝
```

**Minimalist WireGuard GUI Manager for Linux**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-GUI-41CD52?style=flat-square&logo=qt&logoColor=white)](https://pypi.org/project/PyQt6/)
[![WireGuard](https://img.shields.io/badge/WireGuard-VPN-88171A?style=flat-square&logo=wireguard&logoColor=white)](https://wireguard.com)
[![Linux](https://img.shields.io/badge/Linux-universal-FCC624?style=flat-square&logo=linux&logoColor=black)](https://kernel.org)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

*Connect. Stay protected. Skip the terminal.*

**[Русский README →](README.md)**

</div>

---

## ✦ About

**Mini VPN** is a compact desktop application for managing WireGuard connections on Linux. No bloated clients, no magic — just a clean PyQt6 interface on top of `wg-quick`.

Built for people tired of typing `sudo wg-quick up ./config.conf` every single time.

> **v2.0** — now with multi-distro support, 7 UI themes, and a bilingual interface (RU / EN).

<div align="center">

| | |
|---|---|
| 🎨 7 themes (Tokyo Night, AMOLED, Violet & more) | ⚡ Instant tunnel switching |
| 🌐 Real-time IP detection | 📡 Background ping monitoring |
| 🔒 Hide IP with one click | 🔁 XDG Autostart support |
| 🛠 Distro auto-detection & dependency installer | 🔇 DNS patch for WireGuard configs |
| 🌍 Bilingual UI (RU / EN) | ⚙ Settings panel |
| 📐 Resizable & remembers window size | 🖥 Works with any terminal emulator |

</div>

---

## 🐧 Supported Distros

| Distribution | Package Manager |
|---|---|
| Arch / Manjaro / EndeavourOS / Garuda / Artix | `pacman` |
| Debian / Ubuntu / Mint / Pop!_OS / Kali / Zorin | `apt` |
| Fedora / RHEL / CentOS / Rocky / AlmaLinux | `dnf` |
| openSUSE Tumbleweed / Leap | `zypper` |
| Void Linux | `xbps` |

The script auto-detects your distro and uses the correct install commands.

---

## ⚡ Quick Start

### Requirements

- Linux (see table above)
- Python 3.10+
- Any terminal emulator (auto-detected: Konsole, Kitty, Alacritty, GNOME Terminal, xterm)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Sokolovskyyy/arch-mini-vpn.git
cd arch-mini-vpn

# 2. Run — on first launch it will offer to install dependencies
python3 mini-vpn.py
```

> **First launch:** the script detects your distro and offers to install `wireguard-tools`, `openresolv`, and `python-requests` via your native package manager. Just click **Yes**.

### GitHub SSH Key (if needed)

```bash
ssh-keygen -t ed25519 -C "your@email.com"
cat ~/.ssh/id_ed25519.pub
```

Add the key on GitHub → **Settings → SSH and GPG keys → New SSH key**.

### WireGuard Configs

Place your `.conf` files in:

```
~/vpn-configs/
├── amsterdam.conf
├── frankfurt.conf
└── singapore.conf
```

They appear in the dropdown immediately.

---

## 🖥 Interface

### Main Window

```
┌──────────────────────────────────────────┬─────┐
│            ✅ ACTIVE: AMSTERDAM          │  ⚙  │
├──────────────────────────────────────────┴─────┤
│            YOUR IP: 185.220.×××.×××            │  ← click to hide/show
│                   Ping: 18 ms                  │
├────────────────────────────────────────────────┤
│  Select server:                                │
│  [ amsterdam                  ▾ ]  [📝]  [📂]  │
├────────────────────────────────────────────────┤
│  🔇 COMMENT OUT DNS IN CONFIG                  │
│                                                │
│  ⚡            CONNECT VPN                     │
│                                                │
│  🛑            DISCONNECT VPN                  │
└────────────────────────────────────────────────┘
```

### Settings Panel (⚙)

```
┌──────────────────────────────────────────┐
│                Settings                  │
├──────────────────────────────────────────┤
│  ☑ Launch at login                       │
│  Language / Язык            [🇬🇧 EN]      │
│  Color theme       [ Tokyo Night    ▾ ]  │
│                                          │
│  🔗 GitHub repository                    │
│  [           Close            ]          │
└──────────────────────────────────────────┘
```

---

## 🎨 Themes

| Theme | Description |
|---|---|
| **Tokyo Night** | Dark blue-violet palette |
| **Light** | Clean light theme |
| **Blue** | Deep ocean-style dark blue |
| **AMOLED** | Pure black for OLED displays |
| **Violet** | Rich vivid purple palette |
| **Soft Pink** | Gentle pastel pink |
| **System** | Follows your desktop theme |

Themes switch instantly — no restart needed.

---

## 🔧 Features

### 📍 IP & Ping Monitoring
A background thread fetches your real IP from `api.ipify.org` and pings `1.1.1.1` every 7 seconds. Click the IP button to hide it — handy for streams or screenshots.

### 📁 Config Management
- **📝** — rename a config right from the UI
- **📂** — open the `~/vpn-configs` folder in your file manager
- The server list updates automatically

### 🔇 DNS Patch
Some WireGuard configs contain a `DNS = ...` line that can conflict with your system resolver. The **Comment out DNS** button prepends `#` to all such lines in the selected config.

```diff
 [Interface]
 PrivateKey = ...
-DNS = 1.1.1.1
+# DNS = 1.1.1.1
```

### 🔁 Autostart
Managed from the ⚙ Settings panel. Creates or removes `~/.config/autostart/mini-vpn.desktop`. Works with any XDG Autostart-compatible DE (KDE, GNOME, XFCE, etc.).

### 🛠 Dependencies
Installed on first launch or on demand:

| Package | Purpose |
|---|---|
| `wireguard-tools` | `wg` and `wg-quick` binaries |
| `openresolv` | DNS resolver management |
| `python-pyqt6` | GUI framework |
| `python-requests` | HTTP requests for IP lookup |

### 🌍 Bilingual Interface
Switch between Russian and English with the **🇷🇺 RU / 🇬🇧 EN** button in Settings. Takes effect instantly — no restart required.

### 📐 Window Size
The window is freely resizable and saves its size between sessions automatically.

---

## 📁 Project Structure

```
arch-mini-vpn/
├── mini-vpn.py           # main script
├── README.md             # (RU)
├── README.en.md          # (EN)
└── ~/vpn-configs/        # place your .conf files here (auto-created)
```

App state is stored in:
```
~/.config/mini-vpn/
├── settings.json         # language, theme, window size
└── .first_run_done       # first-run flag
```

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first.

```bash
git checkout -b feature/my-feature
git commit -m "feat: add cool feature"
git push origin feature/my-feature
```

---

## 📄 License

Distributed under the **MIT** License. See [LICENSE](LICENSE) for details.

---

<div align="center">

Built with ☕ and `wg-quick` on Linux

*If this project helped you — drop a ⭐*

</div>
