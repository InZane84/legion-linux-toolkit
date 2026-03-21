<p align="center">
  <img src="logo.png" width="90" alt="Legion Linux Toolkit Logo"/>
</p>

<h1 align="center">Legion Linux Toolkit</h1>

<p align="center">
  <strong>A native Linux power management dashboard for Lenovo Legion laptops</strong><br/>
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

## 🖥️ Hardware Target

| | |
|---|---|
| **Model** | Lenovo Legion 5 15ACH6H (2021) |
| **CPU** | AMD Ryzen 7 5800H |
| **GPU** | NVIDIA RTX 3060 (Laptop) + AMD iGPU |
| **OS** | CachyOS / Arch Linux |
| **Desktop** | KDE Plasma 6 — Wayland |

> Other Legion 5/7 models with `ideapad_acpi` should work with minor adjustments.

---

## ✨ Features

### 🏠 Home
- ⚡ Power Mode dropdown — Quiet / Balanced / Performance / Custom (also via Fn+Q)
- 🔋 Battery Mode — Normal / Conservation (~60%) / Rapid Charge
- 🎮 GPU Working Mode — Hybrid / NVIDIA / Integrated (via envycontrol, reboot required)
- 🔄 G-Sync & Display Overdrive toggles
- 🔌 Always on USB & Fn Lock toggles
- 📊 Live CPU & GPU stats — utilization, clock, temperature, fan RPM, VRAM

### 🔋 Battery
- 📈 Live battery %, voltage, health, charge cycles, power draw
- ⚙️ Charging mode controls — Conservation, Rapid Charge, USB Charging
- 🌡️ Live battery temperature (scans all hwmon sources automatically)

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
- ✅ Status feedback — shows applying / applied with tick mark

### ⚙️ System
- 🔒 Fn Lock, Super Key, Touchpad, Camera toggles
- 🎨 Theme selector — Dark / Dark Dimmed / OLED Black

### 🚀 Overclock
- 🔛 Master OC enable/disable toggle — hides all controls when OFF, applies saved settings when ON
- 🔧 CPU max/min frequency + TDP (PL1/PL2) sliders
- 🎮 GPU core offset, memory offset, power limit, temp target

### 🌀 Fan
- 🎡 **Animated fan icons** — 3-blade spinning widget, speed driven by actual RPM in real time
- 🌡️ Auto mode — firmware thermal curves (recommended)
- 💨 Full Speed mode — locks both fans to 100%
- ℹ️ Fan curves per power profile — change aggressiveness via Power Mode

### 🎯 Actions
- 🔁 Auto profile switching on AC connect / battery disconnect

### 🔔 System Tray
- 🔴 Legion Y-blade logo icon with profile colour dot indicator
- ⚡ Quick profile switching without opening dashboard
- 🖱️ Left-click opens dashboard, middle-click cycles profiles

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

**Optional — installed automatically by `install.sh`:**

| Package | Manager | Feature |
|---------|---------|---------|
| `lenovolegionlinux` + `lenovolegionlinux-dkms` | `pacman` | Fan RPM, hardware sysfs, thermalmode, overdrive |
| `envycontrol` | `paru` | GPU mode switching (Hybrid / NVIDIA / Integrated) |
| `legionaura` | `yay` | Keyboard RGB colour control |

---

## 🚀 Install

```bash
git clone https://github.com/v4cachy/legion-linux-toolkit
cd legion-linux-toolkit
sudo bash install.sh
```

> The installer automatically detects your hardware, installs all dependencies, enables the systemd daemon and **launches the tray icon** — no logout or manual step needed.

---

## 🔄 Update

```bash
sudo bash update.sh
```

Pulls the latest commits from GitHub, reinstalls all files, restarts the daemon and relaunches the tray automatically. Shows exactly which commits were pulled.

---

## 🗑️ Uninstall

```bash
sudo bash uninstall.sh
```

Removes every file `install.sh` placed on the system — systemd service, udev rules, polkit policy, autostart entry, CLI and optionally user config.

---

## 🐛 Bug Fixes (v0.6.1 — 20260320)

- 🔧 Fixed RGB keyboard status stuck on "Applying…" — now shows ✓ Applied
- 🔧 Fixed Performance profile colour (was pink, now correctly red)
- 🔧 Fixed GPU Working Mode combo — now uses envycontrol for real switching
- 🔧 Fixed tray icon showing letter circle instead of Legion Y-blade logo
- 🔧 Fixed `QBrush` NameError crashing tray on startup
- 🔧 Fixed dashboard not launching — FanPage methods deleted during refactor
- 🔧 Fixed battery temperature always showing `—`
- 🔧 Fixed OC page crash — orphaned variables before class definition
- 🔧 Fixed VRR toggle snapping back after user interaction
- 🔧 Removed broken Manual PWM fan controls (not supported by this driver)
- 🔧 Fixed display brightness not detected in Hybrid mode (`nvidia_wmi_ec_backlight`)
- 🔧 Fixed install.sh — tray now auto-launches after installation completes

---

## 🆕 What's New (v0.6.1)

- 🎡 **Animated fan icons** — real-time spinning widget driven by actual fan RPM
- 🏠 **Home page redesigned** — LLT-style two-column Power + Graphics cards with dropdowns
- 🖥️ **Display page** — VRR removed, separate Resolution and Refresh Rate selectors added
- 🚀 **OC master toggle** — enable/disable all overclock settings with one switch
- 🎨 **Theme selector** — Dark / Dark Dimmed / OLED Black (replaces accent colour picker)
- 🌀 **Fan page simplified** — Auto / Full Speed only (manual PWM not available on driver)
- 🔴 **Legion logo** — Y-blade icon in tray and dashboard title bar
- 📦 **install.sh** — auto-detects hardware paths, installs all deps, launches tray on completion
- 🔄 **update.sh** — pulls from GitHub, shows commit log, restarts everything automatically

---

## ⚠️ Known Limitations

- **Manual fan PWM** — not available on this driver version; fan curves are firmware-managed per power profile
- **Instant Boot / Flip to Start** — BIOS-only features, not exposed by the Linux driver
- **Display brightness** — requires a backlight node; auto-detected at runtime

---

## 📄 License

MIT — free to use, modify and distribute.

---

<p align="center">Made with ❤️ for Linux on Lenovo Legion</p>
