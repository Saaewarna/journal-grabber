how to use journal grabber

1. Masuk ke folder project

2. Buat virtual environment (biar clean)
python -m venv venv
source venv/bin/activate   # kalau Linux/Mac
venv\Scripts\activate      # kalau Windows

3. Run pake python.exe -m pip install --upgrade pip

4. Run pake pip install -r requirements.txt

python login_tester.py \
--url https://namadomain.com/akseslogin \
--user_field "form[action*='login'] input[name='username']" \
--pass_field "form[action*='login'] input[name='password']" \
--wordlist wordlist.txt \
--auto_discover \
--target_paths "submissions,manager/setup/1,management/settings/website" \
--delay 2 \
--headless

setelah selesai running diatas, result nya bisa dicek di success_log.txt
