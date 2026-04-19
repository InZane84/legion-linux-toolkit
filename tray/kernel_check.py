# Kernel version tracking for LLL compatibility
# Auto-detects by actually checking if LLL works - no manual list needed!

from pathlib import Path
import subprocess

_kernel_check_result = {"checked": False, "works": None}

def get_kernel_version() -> str:
    """Get current kernel version using uname."""
    try:
        result = subprocess.run(["uname", "-r"], capture_output=True, text=True, timeout=3)
        return result.stdout.strip()
    except:
        try:
            return Path("/proc/sys/kernel/osrelease").read_text().split()[0]
        except:
            return "unknown"

def _try_load_lll() -> bool:
    """Try to load LLL module and check if it works."""
    try:
        # Try loading with force
        subprocess.run(["pkexec", "modprobe", "legion_laptop", "force=1"], 
                     capture_output=True, timeout=10)
        # Check if device is bound
        for base in [Path("/sys/class/hwmon"), Path("/sys/devices/virtual/hwmon")]:
            if not base.exists():
                continue
            for p in base.iterdir():
                nf = p / "name"
                if nf.exists() and "legion" in nf.read_text().strip().lower():
                    return True
        return False
    except:
        return False

def check_lll_works() -> bool:
    """Check if LLL actually works on current kernel."""
    global _kernel_check_result
    
    # Already checked this session?
    if _kernel_check_result["checked"]:
        return _kernel_check_result["works"]
    
    # Check if already loaded
    if Path("/sys/module/legion_laptop").exists():
        # Check if device bound
        for base in [Path("/sys/class/hwmon"), Path("/sys/devices/virtual/hwmon")]:
            if not base.exists():
                continue
            for p in base.iterdir():
                nf = p / "name"
                if nf.exists() and nf.read_text().strip() == "legion_hwmon":
                    _kernel_check_result = {"checked": True, "works": True}
                    return True
    
    # Not loaded - try loading once
    works = _try_load_lll()
    _kernel_check_result = {"checked": True, "works": works}
    return works

def get_fan_status_message() -> str:
    """Get dynamic status message - auto-updates based on actual kernel!"""
    kver = get_kernel_version()
    works = check_lll_works()
    
    if works:
        return f"✅ LLL active — Kernel {kver}"
    else:
        # Check if module exists at all
        if Path("/sys/module/legion_laptop").exists():
            return f"⚠️ LLL loaded but no device — Kernel {kver}"
        else:
            return f"⚠️ LLL not available — Kernel {kver}"
