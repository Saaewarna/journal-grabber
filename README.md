Journal Grabber

Simple Playwright-based login tester / journal checker — buat authorized testing aja.

⚠️ JANGAN pake tool ini ke situs yang bukan milikmu atau tanpa izin. Bisa ilegal. Use responsibly.

🔥 Ringkasan singkat

Baca wordlist.txt (username:password per baris).

Buka halaman login dengan Playwright.

Submit kredensial & cek beberapa target_paths (mis. submissions, manager/setup/1, dll).

Kalau sampai halaman penting → tulis ke success_log.txt.

✅ Prereqs

Python 3.8+

Terminal (Windows / Linux / macOS)

Izin untuk test target (MUST HAVE)

🛠️ Setup cepat (Windows)

Masuk folder project:

cd journal-grabber


Buat dan aktifin virtualenv:

python -m venv venv
venv\Scripts\activate


Upgrade pip:

python -m pip install --upgrade pip


Install deps:

pip install -r requirements.txt


Install Playwright browsers:

python -m playwright install chromium
# atau full:
# python -m playwright install

🛠️ Setup cepat (Linux / macOS)
cd journal-grabber
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium

📦 Minimal requirements.txt

Pastikan file tersebut setidaknya berisi:

playwright
rich
pyfiglet


(tambahkan: requests, beautifulsoup4, pandas, lxml jika project butuh)

📄 Wordlist format (wordlist.txt)

Contoh:

alice:Password123
bob:qwerty
john:secretpass


Hanya baris yang mengandung : yang akan diproses.

▶️ Cara menjalankan
1) Mode Interactive (direkomendasi)

Jalankan (tanpa argumen) — tampil UI prompt:

python main.py


Isi prompt sesuai petunjuk. Contoh jawaban yang aman:

Target login URL: https://e-journal.example.edu/index/en/login

Username selector: input[name="username"]

Password selector: input[name="password"]

Wordlist: wordlist.txt

Submit selector: text=Login (atau button[type="submit"])

Headless: y (no UI) / n (lihat browser)

Journals: kosongkan (Enter)

Auto-discover journals?: y

Target paths: submissions,manager/setup/1,management/settings/website (default)

Hasil sukses akan ditulis ke success_log.txt.

2) Mode CLI (langsung pake argumen)
python main.py \
  --url "https://e-journal.example.edu/index/en/login" \
  --user_field "input[name='username']" \
  --pass_field "input[name='password']" \
  --wordlist "wordlist.txt" \
  --submit_selector "text=Login" \
  --auto_discover \
  --headless


Windows single-line example:

python main.py --url "https://.../login" --user_field "input[name='username']" --pass_field "input[name='password']" --wordlist wordlist.txt --submit_selector "text=Login" --auto_discover --headless

ℹ️ Important fields (singkat)

--url → full login URL (ex: https://host/index/en/login)

--user_field, --pass_field → CSS selectors (ex: input[name="username"])

--submit_selector → Playwright text or CSS (ex: text=Login / button[type="submit"])

--wordlist → path ke username:password file

--journals → comma-separated contexts (optional). Biarkan kosong + pakai --auto_discover jika ragu.

--target_paths → comma-separated relative paths (bukan URL penuh). Default:

submissions,manager/setup/1,management/settings/website


Full URL yang dicek = {origin}/index.php/{journal}/{target_path}

🐞 Common errors & quick fixes

ModuleNotFoundError: No module named 'playwright'
→ pip install -r requirements.txt (pastikan venv aktif)

BrowserType.launch: Executable doesn't exist ... headless_shell.exe
→ python -m playwright install atau python -m playwright install chromium

FileNotFoundError: No such file or directory: 'y'
→ Jangan isi y di prompt yang minta file path. Kosongkan jika nggak pakai file.

Selector mismatch → Pesan: Cannot submit login (selector mismatch)
→ Periksa selector di DevTools (F12). Pakai input[name="..."], #id, text=....

Script skip banyak creds (4xx/5xx)
→ Tambah --cooldown / --delay atau set headless=false untuk debugging.

📥 Output

success_log.txt — berisi baris:

username:password -> https://.../index.php/<journal>/<path>


(sudah disaring: hanya log saat sampai ke halaman penting seperti manager/setup/1 atau management/settings/website)

⚖️ Ethics & legal

Tool ini dibuat untuk authorized security testing / admin automation only.
Jangan gunakan untuk brute-force situs yang bukan milikmu atau tanpa izin. Gw nggak bantu kalo dipake buat hal jahat.

🧰 Bonus: Quick checklist (copy-paste)
[ ] cd journal-grabber
[ ] venv\Scripts\activate  # or source venv/bin/activate
[ ] python -m pip install --upgrade pip
[ ] pip install -r requirements.txt
[ ] python -m playwright install chromium
[ ] prepare wordlist.txt (username:password)
[ ] python main.py   # pilih interactive atau pakai args
