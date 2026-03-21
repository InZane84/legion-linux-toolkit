#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════════
# Legion Linux Toolkit — Uninstaller  v0.6.1-BETA
# Removes everything install.sh placed on the system.
# ══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
ok()   { echo -e "  ${GREEN}✓${NC}  $*"; }
warn() { echo -e "  ${YELLOW}⚠${NC}  $*"; }
info() { echo -e "  ${CYAN}→${NC}  $*"; }

[[ $EUID -ne 0 ]] && exec sudo bash "$0" "$@"

echo -e "\n${BOLD}╔══════════════════════════════════════════╗"
echo      "║   Legion Linux Toolkit — Uninstaller     ║"
echo      "║              v0.6.1-BETA                 ║"
echo -e   "╚══════════════════════════════════════════╝${NC}\n"

read -rp "  Remove Legion Linux Toolkit completely? [y/N] " ans
[[ "${ans,,}" == "y" ]] || { echo "  Cancelled."; exit 0; }
echo ""

# ── 1. Kill running processes ─────────────────────────────────────────────────
info "Stopping running instances…"
pkill -f "legion-tray.py"    2>/dev/null && ok "legion-tray stopped"    || true
pkill -f "legion-gui.py"     2>/dev/null && ok "legion-gui stopped"     || true
pkill -f "legion-daemon.py"  2>/dev/null && ok "legion-daemon stopped"  || true
sleep 0.4

# ── 2. Systemd service ────────────────────────────────────────────────────────
info "Removing systemd service…"
systemctl stop    legion-toolkit.service  2>/dev/null || true
systemctl disable legion-toolkit.service  2>/dev/null || true
rm -f /etc/systemd/system/legion-toolkit.service
systemctl daemon-reload
ok "Service removed"

# ── 3. udev rules ─────────────────────────────────────────────────────────────
info "Removing udev rules…"
rm -f /etc/udev/rules.d/99-legion-toolkit.rules
rm -f /etc/udev/rules.d/99-legion-rgb.rules
udevadm control --reload-rules && udevadm trigger
ok "udev rules removed"

# ── 4. Installed files ────────────────────────────────────────────────────────
info "Removing installed files…"
rm -rf /usr/lib/legion-toolkit
ok "/usr/lib/legion-toolkit removed"
rm -f /usr/local/bin/legion-ctl
ok "legion-ctl removed"
rm -f /usr/share/polkit-1/actions/org.legion-toolkit.policy
ok "Polkit policy removed"
rm -f /etc/xdg/autostart/legion-toolkit.desktop
ok "Autostart entry removed"
rm -f /var/log/legion-toolkit.log
rm -f /run/legion-toolkit.sock
ok "Log and socket removed"

# ── 5. User config ────────────────────────────────────────────────────────────
echo ""
read -rp "  Remove per-user config and hardware profile? [y/N] " ans2
if [[ "${ans2,,}" == "y" ]]; then
    for homedir in /home/*/; do
        cfg="${homedir}.config/legion-toolkit"
        if [[ -d "$cfg" ]]; then
            rm -rf "$cfg"
            ok "Removed $cfg"
        fi
    done
    [[ -d /root/.config/legion-toolkit ]] \
        && rm -rf /root/.config/legion-toolkit \
        && ok "Removed /root/.config/legion-toolkit"
else
    warn "User config kept at ~/.config/legion-toolkit"
    warn "(Includes hardware.json, language.json, overclock.json, actions.json)"
fi

echo -e "\n${GREEN}${BOLD}✓ Legion Linux Toolkit completely removed.${NC}\n"
