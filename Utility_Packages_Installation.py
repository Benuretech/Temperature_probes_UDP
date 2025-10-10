"""
This script installs a set of utility packages required for the application.
It checks if pip is installed, upgrades it if necessary, and installs the packages.
It also reports installed vs latest versions for each package.
"""

import subprocess
import os
import sys
import importlib
import json
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

from Setup.Rooth_Path_Finder import rooth_path_finder

# Mapping pip package names to their Python import names
package_import_map = {
    "pySMART": "pySMART",
    "libusb1": "libusb1",
    "lxml": "lxml",
    "pyusb": "usb",
    "pandas": "pandas",
    "scipy": "scipy",
    "numpy": "numpy",
    "dvg-ringbuffer": "dvg_ringbuffer",
    "pyqtgraph": "pyqtgraph",
    "matplotlib": "matplotlib",
    "python-docx": "docx",
    "openpyxl": "openpyxl",
    "psutil": "psutil",
    "SQLAlchemy": "sqlalchemy",
    "xlsxwriter": "xlsxwriter",
    "PyQt6": "PyQt6",
    "crc": "crc",
    "paho-mqtt": "paho",
}

PACKAGES_DIR = os.path.join(rooth_path_finder(), "packages")
os.makedirs(PACKAGES_DIR, exist_ok=True)
if PACKAGES_DIR not in sys.path:
    sys.path.insert(0, PACKAGES_DIR)

def check_pip():
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools"],
                       check=True)
        print("Successfully upgraded pip and setuptools.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred upgrading pip/setuptools: {e}")

def is_package_installed_locally(pip_name: str) -> bool:
    # Heuristic: look for a directory starting with the normalized project name
    # inside PACKAGES_DIR. This is only a quick short-circuit; we still verify later.
    n = pip_name.replace("-", "_").lower()
    try:
        for entry in os.listdir(PACKAGES_DIR):
            if entry.lower().startswith(n):
                return True
    except FileNotFoundError:
        return False
    return False

def install_package(pip_name: str) -> bool:
    if is_package_installed_locally(pip_name):
        print(f"{pip_name} appears to be installed in local packages (will still verify).")
        return True

    print(f"Installing {pip_name} to local packages directory...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", pip_name, f"--target={PACKAGES_DIR}"
        ])
        print(f"{pip_name} has been successfully installed to {PACKAGES_DIR}.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {pip_name}: {e}")
        return False

def verify_import(pip_name: str) -> bool:
    """Verify that the module is importable (using import name)."""
    import_name = package_import_map.get(pip_name, pip_name.replace("-", "_"))
    try:
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False

# ---------- Version helpers ----------
def _installed_version_via_metadata(pip_name: str):
    """
    Try to get installed version via importlib.metadata, searching sys.path and PACKAGES_DIR.
    Returns a string version or None.
    """
    try:
        # Python 3.8+: importlib.metadata in stdlib; 3.10+ recommended
        from importlib.metadata import version, PackageNotFoundError, distributions
    except Exception:
        try:
            # Fallback for very old Pythons
            from importlib_metadata import version, PackageNotFoundError, distributions  # type: ignore
        except Exception:
            version = None
            distributions = None
            PackageNotFoundError = Exception  # best effort

    norm = pip_name  # distribution names are case-insensitive
    if version:
        try:
            return version(norm)
        except Exception:
            # Try scanning distributions on PACKAGES_DIR explicitly
            pass

    if distributions:
        try:
            for dist in distributions(path=[PACKAGES_DIR]):
                # Compare normalized distribution names (case-insensitive)
                if (getattr(dist, "metadata", None) and
                    dist.metadata.get("Name", "").lower() == norm.lower()):
                    return dist.version
                # Some metadata impls use .metadata["Name"]; others use .metadata['name']
                if (getattr(dist, "metadata", None) and
                    dist.metadata.get("name", "").lower() == norm.lower()):
                    return dist.version
        except Exception:
            pass

    return None

def get_installed_version(pip_name: str) -> str | None:
    """
    Best-effort installed version. First via metadata (distribution name),
    falling back to importing and asking __version__ if present.
    """
    v = _installed_version_via_metadata(pip_name)
    if v:
        return v

    # Fallback: import module and read __version__ if present
    import_name = package_import_map.get(pip_name, pip_name.replace("-", "_"))
    try:
        mod = importlib.import_module(import_name)
        v = getattr(mod, "__version__", None)
        if v:
            return str(v)
    except Exception:
        pass
    return None

def get_latest_version_from_pypi(pip_name: str, timeout: float = 5.0) -> str | None:
    """
    Query PyPI's JSON API for the latest version of a project.
    Returns None if offline or project not found.
    """
    url = f"https://pypi.org/pypi/{pip_name}/json"
    try:
        with urlopen(url, timeout=timeout) as resp:
            data = json.load(resp)
        return data.get("info", {}).get("version")
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return None

# ---------- Main ops ----------
def install_all_packages():
    for pip_name in package_import_map:
        install_package(pip_name)

def check_all_installations():
    not_installed = []
    for pip_name in package_import_map:
        ok = verify_import(pip_name)
        if not ok:
            not_installed.append(pip_name)

    if not_installed:
        print("\nThe following packages were not successfully installed or importable:")
        for package in not_installed:
            print("  -", package)
    else:
        print("\nAll packages appear importable.")

def print_versions_report():
    """
    Print a compact table: package | installed | latest | status
    """
    rows = []
    name_w = max(len(n) for n in package_import_map) + 2
    for pip_name in package_import_map:
        installed = get_installed_version(pip_name) or "—"
        latest = get_latest_version_from_pypi(pip_name) or "—"
        status = "up-to-date"
        try:
            # Compare if both are real semantic versions (best-effort lex compare).
            # We avoid packaging.version import to keep no extra deps.
            if installed != "—" and latest != "—" and installed != latest:
                status = "update available"
        except Exception:
            status = "unknown"
        rows.append((pip_name, installed, latest, status))

    # Pretty print
    header = f"{'Package'.ljust(name_w)}  {'Installed':<15} {'Latest':<15} Status"
    print("\nVersion report:")
    print(header)
    print("-" * len(header))
    for pip_name, installed, latest, status in rows:
        print(f"{pip_name.ljust(name_w)}  {installed:<15} {latest:<15} {status}")

if __name__ == "__main__":
    check_pip()
    install_all_packages()
    print("\n\n*****************************\n")
    print("Verifying installations...")
    check_all_installations()
    print_versions_report()