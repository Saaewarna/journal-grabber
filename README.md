# 📘 Journal Grabber

**Simple Playwright-based login tester / journal checker — authorized testing only.**

> ⚠️ **WARNING:**  
> Jangan pake tool ini ke situs yang bukan milikmu atau tanpa izin. Bisa ilegal. Use responsibly.

---

## 🔥 Ringkasan Singkat
1. Baca `wordlist.txt` (`username:password` per baris).  
2. Login via Playwright.  
3. Cek `target_paths` (mis: `submissions`, `manager/setup/1`, dll).  
4. Kalau sampai halaman penting → tulis ke `success_log.txt`.  

---

## ✅ Prereqs
- Python 3.8+  
- Terminal (Windows / Linux / macOS)  
- Izin untuk test target (MUST HAVE)

---

## 🛠️ Setup Cepat

### Windows
```bash
cd journal-grabber
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium

```
### Linux / macOS
```bash
cd journal-grabber
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium

```
📦 Minimal requirements.txt
```bash
playwright
rich
pyfiglet
requests
beautifulsoup4
lxml
pandas

```
📄 Wordlist format
```bash
alice:Password123
bob:qwerty
john:secretpass

```
▶️ Cara Menjalankan
```bash
python main.py
```
A) Mode Interactive (direkomendasi)
Isi prompt contoh:

URL: https://namaweb.com/index/login
user_field: input[name="username"]
pass_field: input[name="password"]
wordlist: wordlist.txt
submit_selector: text=Login (atau button[type="submit"] kalau teksnya beda)
success_selector: (biarin kosong dulu)
success_text: (biarin kosong dulu)
headless: y atau n sesuai selera
journals: (kosong)
auto_discover: y

B) Mode CLI
python main.py \
  --url "https://e-journal.example.edu/index/en/login" \
  --user_field "input[name='username']" \
  --pass_field "input[name='password']" \
  --wordlist "wordlist.txt" \
  --submit_selector "text=Login" \
  --auto_discover \
  --headless
