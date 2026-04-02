#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════════
# Legion Linux Toolkit — Nuitka Build Script
# Compiles legion-gui.py and legion-tray.py into standalone binaries
# ══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'
YELLOW='\033[1;33m'; BOLD='\033[1m'; NC='\033[0m'
ok()   { echo -e "  ${GREEN}✓${NC}  $*"; }
info() { echo -e "  ${CYAN}→${NC}  $*"; }
warn() { echo -e "  ${YELLOW}⚠${NC}  $*"; }
err()  { echo -e "  ${RED}✗${NC}  $*"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRAY_SRC="$SCRIPT_DIR/tray/legion-tray.py"
GUI_SRC="$SCRIPT_DIR/tray/legion-gui.py"
OUT_DIR="$SCRIPT_DIR/dist"

echo -e "\n${BOLD}╔══════════════════════════════════════════╗"
echo      "║   Legion Linux Toolkit — Build           ║"
echo      "║   Nuitka → Standalone Binaries           ║"
echo -e   "╚══════════════════════════════════════════╝${NC}\n"

# ── 1. Check Nuitka ──────────────────────────────────────────────────────────
echo -e "${BOLD}[1/5] Checking Nuitka…${NC}"
if ! python3 -m nuitka --version &>/dev/null; then
    info "Nuitka not found — installing…"
    pip install nuitka --break-system-packages \
        || err "Failed to install Nuitka. Try: pip install nuitka --break-system-packages"
fi
NUITKA_VER=$(python3 -m nuitka --version 2>/dev/null | head -1)
ok "Nuitka ready — $NUITKA_VER"

# ── 2. Check dependencies ─────────────────────────────────────────────────────
echo -e "${BOLD}[2/5] Checking dependencies…${NC}"
python3 -c "import PyQt6" 2>/dev/null || err "python-pyqt6 not installed"
ok "PyQt6 found"
command -v patchelf &>/dev/null || {
    warn "patchelf not found — installing (needed by Nuitka)"
    pacman -S --noconfirm --needed patchelf 2>/dev/null || true
}

# ── 3. Prepare output directory ───────────────────────────────────────────────
echo -e "${BOLD}[3/5] Preparing output…${NC}"
mkdir -p "$OUT_DIR"
ok "Output directory: $OUT_DIR"

# Common Nuitka flags
COMMON_FLAGS=(
    --onefile
    --enable-plugin=pyqt6
    --assume-yes-for-downloads
    --output-dir="$OUT_DIR"
    --linux-icon="$SCRIPT_DIR/logo.png"
    --nofollow-import-to=tkinter
    --nofollow-import-to=unittest
    --nofollow-import-to=test
    --python-flag=no_docstrings
    --python-flag=no_asserts
    --quiet
)

# ── 4. Build GUI (legion-gui) ─────────────────────────────────────────────────
echo -e "${BOLD}[4/5] Compiling legion-gui (dashboard)…${NC}"
info "This takes 3–8 minutes on first build…"

python3 -m nuitka \
    "${COMMON_FLAGS[@]}" \
    --output-filename=legion-gui \
    --windows-disable-console \
    "$GUI_SRC" 2>&1 | grep -v "^Nuitka:" | grep -v "^$" || true

if [[ -f "$OUT_DIR/legion-gui" ]]; then
    chmod +x "$OUT_DIR/legion-gui"
    SIZE=$(du -sh "$OUT_DIR/legion-gui" | cut -f1)
    ok "legion-gui built → $OUT_DIR/legion-gui  ($SIZE)"
else
    err "legion-gui build failed — check output above"
fi

# ── 5. Build tray (legion-tray) ───────────────────────────────────────────────
echo -e "${BOLD}[5/5] Compiling legion-tray…${NC}"
info "This takes 2–5 minutes…"

python3 -m nuitka \
    "${COMMON_FLAGS[@]}" \
    --output-filename=legion-tray \
    "$TRAY_SRC" 2>&1 | grep -v "^Nuitka:" | grep -v "^$" || true

if [[ -f "$OUT_DIR/legion-tray" ]]; then
    chmod +x "$OUT_DIR/legion-tray"
    SIZE=$(du -sh "$OUT_DIR/legion-tray" | cut -f1)
    ok "legion-tray built → $OUT_DIR/legion-tray  ($SIZE)"
else
    err "legion-tray build failed — check output above"
fi

# ── Done ─────────────────────────────────────────────────────────────────────
echo -e "\n${GREEN}${BOLD}✓ Build complete!${NC}"
echo ""
echo    "  Binaries in: $OUT_DIR/"
ls -lh "$OUT_DIR/legion-gui" "$OUT_DIR/legion-tray" 2>/dev/null | \
    awk '{print "    "$NF"  "$5}'
echo ""
echo    "  Test the binaries:"
echo -e "    ${CYAN}$OUT_DIR/legion-tray &${NC}"
echo -e "    ${CYAN}$OUT_DIR/legion-gui${NC}"
echo ""
echo    "  To install the built binaries instead of the Python scripts:"
echo -e "    ${CYAN}sudo bash install-binary.sh${NC}"
echo ""
