# 📘 Journal Grabber

**Simple Playwright-based login tester / journal checker — buat authorized testing aja.**

⚠️ **WARNING:**  
JANGAN pake tool ini ke situs yang bukan milikmu atau tanpa izin. Bisa ilegal. Use responsibly.  

---

## 🔥 Ringkasan Singkat
1. Baca `wordlist.txt` (`username:password` per baris).  
2. Buka halaman login dengan Playwright.  
3. Submit kredensial & cek beberapa `target_paths` (misalnya: `submissions`, `manager/setup/1`, dll).  
4. Kalau sampai halaman penting → tulis ke `success_log.txt`.  

---

## ✅ Prereqs
- Python 3.8+  
- Terminal (Windows / Linux / macOS)  
- Izin untuk test target (**MUST HAVE**)  

---

## 🛠️ Setup Cepat

### 1) Windows
```bash
# masuk folder project
cd journal-grabber

# buat virtual environment + aktifkan
python -m venv venv
venv\Scripts\activate

# upgrade pip
python -m pip install --upgrade pip

# install dependencies
pip install -r requirements.txt

# install browser Playwright
python -m playwright install chromium
# atau full:
# python -m playwright install
