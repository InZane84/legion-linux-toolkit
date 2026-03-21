<p align="center">
  <img src="logo.png" width="90" alt="Legion Linux Toolkit Logo"/>
</p>

<h1 align="center">Legion Linux Toolkit</h1>

<p align="center">
  <strong>A native Linux power management dashboard for Lenovo laptops</strong><br/>
  Built for CachyOS · KDE Plasma 6 · Wayland
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-v0.6.1--BETA-red?style=flat-square"/>
  <img src="https://img.shields.io/badge/build-20260320-orange?style=flat-square"/>
  <img src="https://img.shields.io/badge/platform-Linux-blue?style=flat-square"/>
  <img src="https://img.shields.io/badge/desktop-KDE%20Plasma%206-purple?style=flat-square"/>
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square"/>
</p>

---

## 🖥️ Supported Hardware

| Brand | Models | Support Level |
|-------|--------|---------------|
| **Legion** | Legion 5, 5 Pro, 7, Slim 5/7 | ✅ Full |
| **LOQ** | LOQ 15, 16 | ✅ Full |
| **ThinkPad** | All modern ThinkPad models | ✅ Full + extras |
| **Yoga** | Yoga 6, 7, 9, Slim series | ✅ Full + extras |
| **IdeaPad** | IdeaPad 5, Flex, Slim series | ✅ Standard |
| **ThinkBook** | ThinkBook 14, 16 series | ✅ Standard |

> Primary development target: **Lenovo Legion 5 15ACH6H (2021)** — AMD Ryzen 7 5800H · NVIDIA RTX 3060 · CachyOS · KDE Plasma 6 Wayland

---

## ✨ Features

### 🏠 Home
- ⚡ Power Mode dropdown — Quiet / Balanced / Performance / Custom (also Fn+Q)
- 🔋 Battery Mode — Normal / Conservation (~60%) / Rapid Charge
- 🎮 GPU Working Mode — Hybrid / NVIDIA / Integrated (via envycontrol, reboot required)
- 🔄 G-Sync & Display Overdrive toggles
- 🔌 Always on USB & Fn Lock toggles
- 📊 Live CPU & GPU stats — utilization, clock, temperature, fan RPM, VRAM

### 🔋 Battery
- 📈 Live battery %, voltage, health, charge cycles, power draw, temperature
- ⚙️ Charging — Conservation (~60%), Rapid Charge, USB Charging, Power Charge Mode
- 🔧 **ThinkPad only** — Start/Stop charge threshold controls (e.g. 40%–80%)

### ⚡ Performance
- 🎛️ CPU governor, AMD boost toggle, EPP selector
- 🌡️ Enhanced thermal mode, fan full speed toggle

### 🖥️ Display
- ☀️ Screen brightness slider — auto-detects backlight path (`nvidia_wmi_ec_backlight`, `amdgpu_bl0`, etc.)
- 📐 Resolution selector — change display resolution instantly via kscreen
- 🔄 Refresh rate selector — change Hz independently from resolution
- ✨ Display Overdrive & G-Sync toggles

### ⌨️ Keyboard RGB
- 🌈 4-zone RGB via LegionAura — Static, Breath, Wave, Hue, Off
- 🎨 Per-zone colour pickers + hex input
- 💡 Quick presets — Legion Red, Ocean, Sunset, Aurora and more
- 🔆 Keyboard backlight brightness slider
- ✅ Live status feedback — shows applying / ✓ applied with tick mark

### ⚙️ System
- 🔒 Fn Lock, Super Key, Touchpad, Camera toggles
- 🎨 Theme — Dark / Dark Dimmed / OLED Black
- 🔄 **Yoga only** — Hinge mode display (Laptop / Tent / Tablet / Stand)
- 💡 **ThinkPad only** — ThinkLight toggle, Mic Mute LED toggle

### 🚀 Overclock
- 🔛 Master OC enable/disable toggle
- 🔧 CPU max/min frequency + TDP (PL1/PL2) sliders
- 🎮 GPU core offset, memory offset, power limit, temp target

### 🌀 Fan
- 🎡 Animated fan icons — 3-blade spin widget, speed driven by actual RPM in real time
- 🌡️ Auto mode — firmware thermal curves (recommended)
- 💨 Full Speed mode — locks both fans to 100%

### 🎯 Actions
- 🔁 Auto profile switching on AC connect / battery disconnect

### 🔔 System Tray
- 🔴 Legion Y-blade logo icon with profile colour dot indicator
- ⚡ Quick profile switching without opening dashboard
- 🖱️ Left-click opens dashboard, middle-click cycles profiles

---

## 🌍 Languages

The setup wizard lets you choose your language on first launch. Supported:

🇬🇧 English · 🇫🇷 Français · 🇩🇪 Deutsch · 🇪🇸 Español · 🇵🇹 Português · 🇹🇷 Türkçe · 🇷🇺 Русский · 🇨🇳 中文 · 🇯🇵 日本語 · 🇰🇷 한국어 · 🇸🇦 العربية

---

## 🎨 Power Profiles

| Profile | Label | Colour | TDP | Fan |
|---------|-------|--------|-----|-----|
| `low-power` | Quiet | 🔵 Blue | 15W | Silent |
| `balanced` | Balanced | ⚪ White | 35W | Auto |
| `balanced-performance` | Performance | 🔴 Red | 45W | Gaming |
| `performance` | Custom | 🩷 Pink | 54W | Max |

---

## 📦 Requirements

**Required — auto-installed by `install.sh`:**
- `python-pyqt6` — GUI framework
- `qt6-wayland` — Wayland support for KDE Plasma 6
- `libnotify` — desktop notifications
- `kscreen` — resolution & refresh rate control
- `git` — for updates via `update.sh`

**Optional — installed automatically based on detected brand:**

| Package | Manager | Brand | Feature |
|---------|---------|-------|---------|
| `lenovolegionlinux` + `lenovolegionlinux-dkms` | `pacman` | Legion / LOQ | Fan RPM, hardware sysfs, thermalmode |
| `envycontrol` | `paru` | Legion / LOQ | GPU mode switching |
| `legionaura` | `yay` | Legion | Keyboard RGB control |
| `fprintd` | `pacman` | ThinkPad / Yoga / ThinkBook | Fingerprint reader |
| `iio-sensor-proxy` | `pacman` | Yoga | Auto screen rotate |

---

## 🚀 Install

```bash
git clone https://github.com/v4cachy/legion-linux-toolkit
cd legion-linux-toolkit
sudo bash install.sh
```

> The installer **auto-detects your Lenovo brand**, installs only the packages relevant to your device, checks all hardware sysfs paths, enables the daemon service and **launches the tray icon automatically** — no logout needed.
>
> On first launch the **setup wizard** appears to choose your language and run a one-time hardware scan.

---

## 🔄 Update

```bash
sudo bash update.sh
```

Pulls latest commits from GitHub, shows exactly what changed, reinstalls all files, restarts the daemon and relaunches the tray automatically. Tag-based version shown at the end.

---

## 🗑️ Uninstall

```bash
sudo bash uninstall.sh
```

Removes every file `install.sh` placed on the system — systemd service, udev rules, polkit policy, autostart entry, CLI binary. Optionally removes per-user config (hardware profile, language, OC settings, actions).

---

## 🆕 What's New (v0.6.1 — 20260320)

- 🌍 **11-language support** — first-run wizard with language picker
- 🔍 **One-time hardware detection** — auto-detects brand, model and capabilities, saved to `hardware.json`
- 🏷️ **Multi-brand support** — Legion, LOQ, ThinkPad, ThinkBook, Yoga, IdeaPad
- 🔧 **ThinkPad charge thresholds** — start/stop % controls in Battery page
- 🔄 **Yoga hinge mode** — mode display in System page
- 💡 **ThinkPad extras** — ThinkLight and Mic Mute LED toggles
- 🎡 **Animated fan icons** — real-time spinning driven by actual RPM
- 🏠 **Home page redesigned** — LLT-style two-column Power + Graphics cards
- 🖥️ **Display page** — separate Resolution and Refresh Rate cards
- 🚀 **OC master toggle** — enable/disable all OC with one switch
- 🔴 **Legion Y-blade logo** — tray icon + sidebar + window title bar
- 🎨 **UI polish** — sidebar logo, brand pill in topbar, styled AC indicator
- 📦 **install.sh** — brand detection, brand-specific packages, wizard flag reset
- 🔄 **update.sh** — GitHub pull with commit log, version display

---

## 🐛 Bug Fixes (v0.6.1)

- 🔧 Fixed RGB keyboard status stuck on "Applying…"
- 🔧 Fixed Performance profile colour (red not pink)
- 🔧 Fixed GPU mode combo — now uses real envycontrol switching
- 🔧 Fixed tray icon showing letter circle instead of Legion Y-blade logo
- 🔧 Fixed `QBrush` NameError crashing tray on startup
- 🔧 Fixed dashboard not launching after FanPage rewrite
- 🔧 Fixed battery temperature always showing `—`
- 🔧 Fixed OC page crash — orphaned variables before class definition
- 🔧 Fixed display brightness not detected in Hybrid mode
- 🔧 Fixed install.sh — tray now auto-launches after install completes

---

## ⚠️ Known Limitations

- **Manual fan PWM** — not available on Legion 5 15ACH6H driver; fan curves are firmware-managed per power profile
- **Instant Boot / Flip to Start** — BIOS-only, not exposed by the Linux driver
- **Display brightness** — requires a backlight node; auto-detected at runtime
- **Dolby Audio / Atmos** — Windows driver only, not available on Linux

---

## 📄 License

MIT — free to use, modify and distribute.

---

<p align="center">Made with ❤️ for Linux on Lenovo</p>
