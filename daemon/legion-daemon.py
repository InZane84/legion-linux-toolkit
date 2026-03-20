#!/usr/bin/env python3
"""
Legion Linux Toolkit — Daemon
Hardware: Lenovo Legion 5 15ACH6H | Ryzen 7 5800H | CachyOS

Responsibilities:
  • Apply CPU governor / boost / EPP / fan on profile change
  • Watch /sys/firmware/acpi/platform_profile (Fn+Q triggers this)
  • Unix socket at /run/legion-toolkit.sock for GUI commands
  • Send desktop notifications on profile change

Profile name note: this machine's firmware uses "low-power" for the quiet
profile. The daemon accepts both "quiet" and "low-power" as input, always
writing the actual firmware value to sysfs.
"""

import os, sys, time, signal, logging, subprocess, socket, threading, glob
from pathlib import Path

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/var/log/legion-toolkit.log", mode="a"),
    ],
)
log = logging.getLogger("legion")

# ── sysfs paths ───────────────────────────────────────────────────────────────
PLATFORM_PROFILE         = Path("/sys/firmware/acpi/platform_profile")
PLATFORM_PROFILE_CHOICES = Path("/sys/firmware/acpi/platform_profile_choices")
AMD_BOOST                = Path("/sys/devices/system/cpu/cpufreq/boost")
RAPL_PL1                 = Path("/sys/class/powercap/intel-rapl:0/constraint_0_power_limit_uw")
RAPL_PL2                 = Path("/sys/class/powercap/intel-rapl:0/constraint_1_power_limit_uw")
GOVERNOR_GLOB            = "/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
EPP_GLOB                 = "/sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference"
IDEAPAD_BASE             = Path("/sys/bus/platform/drivers/ideapad_acpi/VPC2004:00")
FAN_MODE                 = IDEAPAD_BASE / "fan_mode"
CONSERVATION_MODE        = IDEAPAD_BASE / "conservation_mode"
CAMERA_POWER             = IDEAPAD_BASE / "camera_power"
FN_LOCK                  = IDEAPAD_BASE / "fn_lock"
USB_CHARGING             = IDEAPAD_BASE / "usb_charging"
RAPID_CHARGE             = Path("/sys/devices/pci0000:00/0000:00:14.3/PNP0C09:00/rapidcharge")
SOCKET_PATH              = Path("/run/legion-toolkit.sock")

# ── Profile settings ──────────────────────────────────────────────────────────
# Keys here must match what we accept from GUI / CLI.
# "low-power" = what this machine's firmware actually calls it.
# "quiet" is an alias handled in _to_fw() below.
PROFILES = {
    "low-power": {
        "label":       "Quiet",
        "description": "Silent · 15W · Boost OFF",
        "governor":    "powersave",
        "boost":       "0",
        "epp":         "power",
        "pl1_uw":      15_000_000,
        "pl2_uw":      20_000_000,
        "fan_mode":    "0",
    },
    "balanced": {
        "label":       "Balanced",
        "description": "Everyday · 35W · Boost ON",
        "governor":    "powersave",
        "boost":       "1",
        "epp":         "balance_performance",
        "pl1_uw":      35_000_000,
        "pl2_uw":      54_000_000,
        "fan_mode":    "0",
    },
    "balanced-performance": {
        "label":       "Performance",
        "description": "Gaming · 45W · Boost ON",
        "governor":    "performance",
        "boost":       "1",
        "epp":         "performance",
        "pl1_uw":      45_000_000,
        "pl2_uw":      54_000_000,
        "fan_mode":    "0",
    },
    "performance": {
        "label":       "Custom",
        "description": "Max Power · 54W · Boost ON",
        "governor":    "performance",
        "boost":       "1",
        "epp":         "performance",
        "pl1_uw":      54_000_000,
        "pl2_uw":      54_000_000,
        "fan_mode":    "0",
    },
}

# Alias map: accept "quiet" from GUI/CLI, translate to firmware "low-power"
_ALIASES = {"quiet": "low-power"}

def _to_fw(name: str) -> str:
    """Translate alias or unknown name to the exact firmware profile name."""
    name = name.strip()
    if name in PROFILES:
        return name
    if name in _ALIASES:
        return _ALIASES[name]
    # Try to find a firmware match from actual choices
    try:
        choices = PLATFORM_PROFILE_CHOICES.read_text().strip().split()
        if name in choices:
            return name
        for c in choices:
            if name in c or c in name:
                return c
    except Exception:
        pass
    return name  # best effort

def get_current_profile() -> str:
    try:
        return PLATFORM_PROFILE.read_text().strip()
    except Exception:
        return "balanced"

def get_choices() -> list[str]:
    try:
        return PLATFORM_PROFILE_CHOICES.read_text().strip().split()
    except Exception:
        return list(PROFILES.keys())

# ── sysfs write helpers ────────────────────────────────────────────────────────
def _write(path: Path, value: str, label: str) -> bool:
    try:
        if not path.exists():
            log.warning(f"  ✗ {label}: path missing ({path})")
            return False
        if not os.access(path, os.W_OK):
            log.warning(f"  ✗ {label}: not writable ({path})")
            return False
        path.write_text(str(value))
        log.info(f"  ✓ {label} → {value}")
        return True
    except Exception as e:
        log.warning(f"  ✗ {label}: {e}")
        return False

def _write_glob(pattern: str, value: str, label: str) -> int:
    paths = glob.glob(pattern)
    ok = 0
    for p in paths:
        try:
            if os.access(p, os.W_OK):
                Path(p).write_text(value)
                ok += 1
        except Exception:
            pass
    if ok:
        log.info(f"  ✓ {label} → {value}  ({ok} cores)")
    else:
        log.warning(f"  ✗ {label}: no writable paths found")
    return ok

def _restore_max_freq():
    for cpu_dir in glob.glob("/sys/devices/system/cpu/cpu[0-9]*/cpufreq"):
        try:
            hw = (Path(cpu_dir) / "cpuinfo_max_freq").read_text().strip()
            mx = Path(cpu_dir) / "scaling_max_freq"
            if mx.exists() and os.access(mx, os.W_OK):
                mx.write_text(hw)
        except Exception:
            pass

def _rapl_available() -> bool:
    return RAPL_PL1.exists() and os.access(RAPL_PL1, os.W_OK)

# ── Apply profile ──────────────────────────────────────────────────────────────
def apply_profile(raw_name: str):
    """Apply all settings for a profile. Accepts alias names like 'quiet'."""
    fw_name = _to_fw(raw_name)

    if fw_name not in PROFILES:
        log.error(f"Unknown profile: {raw_name!r} (resolved: {fw_name!r})")
        log.error(f"Available: {', '.join(PROFILES.keys())}")
        return

    p = PROFILES[fw_name]
    log.info("")
    log.info(f"══ {p['label']} ({fw_name}) ══  {p['description']}")
    log.info("")

    # 1. Write platform_profile — use EXACT firmware name
    _write(PLATFORM_PROFILE, fw_name, "platform_profile")

    # 2. Restore CPU max freq (clear any cap from previous profile)
    _restore_max_freq()
    log.info("  ✓ CPU max freq → hardware max")

    # 3. CPU governor
    _write_glob(GOVERNOR_GLOB, p["governor"], f"governor")

    # 4. AMD boost
    _write(AMD_BOOST, p["boost"], "AMD boost")

    # 5. EPP
    _write_glob(EPP_GLOB, p["epp"], "EPP")

    # 6. RAPL TDP (optional — needs ryzen_smu)
    if _rapl_available():
        _write(RAPL_PL1, str(p["pl1_uw"]), f"TDP PL1 ({p['pl1_uw']//1_000_000}W)")
        _write(RAPL_PL2, str(p["pl2_uw"]), f"TDP PL2 ({p['pl2_uw']//1_000_000}W)")
    else:
        log.info("  ⏭ TDP skipped (install ryzen_smu-dkms-git to enable)")

    # 7. Fan mode
    _write(FAN_MODE, p["fan_mode"], "fan_mode")

    # 8. Thermal mode LED indicator (lenovo-legion-linux driver)
    # This controls the profile indicator light on the laptop:
    # 0 = quiet/blue-dim, 1 = balanced/white, 2 = performance+, 3 = performance
    _thermalmode = {
        "low-power":            "0",
        "balanced":             "1",
        "balanced-performance": "2",
        "performance":          "3",
    }
    _LEGION_BASE = Path("/sys/devices/pci0000:00/0000:00:14.3/PNP0C09:00")
    _thermal_path = _LEGION_BASE / "thermalmode"
    if _thermal_path.exists() and fw_name in _thermalmode:
        _write(_thermal_path, _thermalmode[fw_name], "thermalmode LED")

    log.info("")

# ── Desktop notification ───────────────────────────────────────────────────────
def _notify(fw_name: str):
    # Labels match Windows Legion software / LenovoLegionLinux
    _labels = {
        "low-power":            "🔵 Quiet",
        "balanced":             "⚪ Balanced",
        "balanced-performance": "🟠 Performance",
        "performance":          "🩷 Custom",
    }
    p = PROFILES.get(fw_name, {})
    label = _labels.get(fw_name, p.get("label", fw_name))
    desc  = p.get("description", "")
    icons = {
        "low-power":            "battery-caution",
        "balanced":             "battery-good",
        "balanced-performance": "battery-full-charged",
        "performance":          "utilities-system-monitor",
    }
    try:
        result = subprocess.run(
            ["loginctl", "list-sessions", "--no-legend"],
            capture_output=True, text=True
        )
        for line in result.stdout.strip().splitlines():
            parts = line.split()
            if len(parts) < 3:
                continue
            session_id, uid, username = parts[0], parts[1], parts[2]
            stype = subprocess.run(
                ["loginctl", "show-session", session_id, "-p", "Type", "--value"],
                capture_output=True, text=True
            ).stdout.strip()
            if stype not in ("wayland", "x11"):
                continue
            dbus = f"/run/user/{uid}/bus"
            if not os.path.exists(dbus):
                continue
            subprocess.Popen([
                "runuser", "-u", username, "--",
                "env",
                f"DBUS_SESSION_BUS_ADDRESS=unix:path={dbus}",
                "notify-send",
                "-i", icons.get(fw_name, "dialog-information"),
                "-t", "2500",
                f"Legion — {label}",
                desc,
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            break
    except Exception as e:
        log.debug(f"Notification skipped: {e}")

# ── Unix socket server ─────────────────────────────────────────────────────────
# Lets the GUI change profiles without pkexec — daemon is already root.
#
# Commands the GUI can send:
#   set:<profile>          → apply profile, respond "ok" or "error:<msg>"
#   write:<path>:<value>   → write any sysfs path, respond "ok" or "error:<msg>"
#   get:profile            → respond "profile:<current>"
#   get:choices            → respond "choices:<space-separated list>"

def _handle_connection(conn: socket.socket):
    try:
        data = conn.recv(256).decode("utf-8", errors="replace").strip()
        if not data:
            return
        log.debug(f"Socket cmd: {data!r}")

        if data.startswith("set:"):
            name = data[4:].strip()
            fw   = _to_fw(name)
            if fw in PROFILES:
                try:
                    PLATFORM_PROFILE.write_text(fw)
                    # Daemon's poll loop will detect the change and apply settings
                    conn.send(b"ok\n")
                    log.info(f"Socket: profile → {fw}")
                except Exception as e:
                    conn.send(f"error:{e}\n".encode())
            else:
                conn.send(f"error:unknown profile {name!r}\n".encode())

        elif data.startswith("write:"):
            # write:/sys/path:value
            _, path_str, value = data.split(":", 2)
            try:
                p = Path(path_str)
                if not p.exists():
                    conn.send(b"error:path not found\n")
                    return
                p.write_text(value.strip())
                conn.send(b"ok\n")
                log.info(f"Socket: write {path_str} → {value.strip()}")
            except Exception as e:
                conn.send(f"error:{e}\n".encode())

        elif data == "get:profile":
            conn.send(f"profile:{get_current_profile()}\n".encode())

        elif data == "get:choices":
            conn.send(f"choices:{' '.join(get_choices())}\n".encode())

        else:
            conn.send(b"error:unknown command\n")

    except Exception as e:
        log.warning(f"Socket handler error: {e}")
    finally:
        conn.close()

def _run_socket_server(stop_event: threading.Event):
    if SOCKET_PATH.exists():
        SOCKET_PATH.unlink()
    try:
        srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        srv.bind(str(SOCKET_PATH))
        SOCKET_PATH.chmod(0o666)  # any user can connect
        srv.listen(8)
        srv.settimeout(1.0)
        log.info(f"Socket ready: {SOCKET_PATH}")
    except Exception as e:
        log.error(f"Socket server failed to start: {e}")
        return

    while not stop_event.is_set():
        try:
            conn, _ = srv.accept()
            t = threading.Thread(target=_handle_connection, args=(conn,), daemon=True)
            t.start()
        except socket.timeout:
            continue
        except Exception as e:
            if not stop_event.is_set():
                log.warning(f"Socket accept error: {e}")

    srv.close()
    if SOCKET_PATH.exists():
        SOCKET_PATH.unlink()
    log.info("Socket server stopped")

# ── Main daemon loop ───────────────────────────────────────────────────────────
class Daemon:
    def __init__(self):
        self._running    = True
        self._stop_event = threading.Event()
        signal.signal(signal.SIGTERM, self._stop)
        signal.signal(signal.SIGINT,  self._stop)

    def _stop(self, *_):
        log.info("Stopping...")
        self._running = False
        self._stop_event.set()

    def run(self):
        log.info("Legion Linux Toolkit daemon starting")
        log.info(f"Firmware profile choices: {' | '.join(get_choices())}")

        if not _rapl_available():
            log.warning("RAPL not writable — TDP limits disabled")
            log.warning("  → install ryzen_smu-dkms-git to enable")

        # Start socket server
        sock_thread = threading.Thread(
            target=_run_socket_server, args=(self._stop_event,),
            daemon=True, name="socket-server"
        )
        sock_thread.start()

        # Apply current profile on startup
        current = get_current_profile()
        log.info(f"Startup profile: {current}")
        apply_profile(current)
        last = current

        # Poll loop — detects Fn+Q and manual profile changes
        log.info("Watching platform_profile (polling 300ms)...")
        while self._running:
            try:
                current = get_current_profile()
                if current != last:
                    log.info(f"Profile changed: {last} → {current}")
                    apply_profile(current)
                    _notify(current)
                    last = current
            except Exception as e:
                log.error(f"Poll error: {e}")
            time.sleep(0.3)

        self._stop_event.set()
        log.info("Daemon stopped")

# ── CLI (one-shot commands called by scripts / tray) ──────────────────────────
def _cli(args):
    cmd = args[0]

    # Profile switch
    if cmd in list(PROFILES.keys()) + list(_ALIASES.keys()):
        apply_profile(cmd)
        return

    dispatch = {
        "status": lambda: (
            print(f"Profile  : {get_current_profile()}"),
            print(f"Choices  : {' '.join(get_choices())}"),
            print(f"Governor : {_read_first('/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor')}"),
            print(f"Boost    : {_read_first(str(AMD_BOOST))}"),
            print(f"EPP      : {_read_first('/sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference')}"),
        ),
        "conservation-on":  lambda: _write(CONSERVATION_MODE, "1", "conservation_mode"),
        "conservation-off": lambda: _write(CONSERVATION_MODE, "0", "conservation_mode"),
        "camera-on":        lambda: _write(CAMERA_POWER, "1", "camera"),
        "camera-off":       lambda: _write(CAMERA_POWER, "0", "camera"),
        "fn-lock-on":       lambda: _write(FN_LOCK, "1", "fn_lock"),
        "fn-lock-off":      lambda: _write(FN_LOCK, "0", "fn_lock"),
        "usb-charging-on":  lambda: _write(USB_CHARGING, "1", "usb_charging"),
        "usb-charging-off": lambda: _write(USB_CHARGING, "0", "usb_charging"),
        "rapid-charge-on":  lambda: _write(RAPID_CHARGE, "1", "rapid_charge"),
        "rapid-charge-off": lambda: _write(RAPID_CHARGE, "0", "rapid_charge"),
    }

    if cmd in dispatch:
        dispatch[cmd]()
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print("Usage: legion-daemon [quiet|balanced|balanced-performance|performance|status]")
        print("       legion-daemon [conservation-on|off|camera-on|off|fn-lock-on|off|...]")
        sys.exit(1)

def _read_first(path: str) -> str:
    try:
        return Path(path).read_text().strip()
    except Exception:
        return "N/A"

# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if os.geteuid() != 0:
        sys.exit("ERROR: must run as root")

    if len(sys.argv) > 1:
        _cli(sys.argv[1:])
    else:
        Daemon().run()
