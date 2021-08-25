1. Зайти на pythonanywhere (креды в гугл доке)
2. Открыть консоль
3. `. ./venv/bin/activate`
4. `cd foodplan`
5. `git pull`
6. `export DJANGO_SETTINGS_MODULE='foodplan.settings'`
7. `PYTHONPATH=. django-admin migrate`
8. `PYTHONPATH=. django-admin collectstatic`
9. Зайти на вкладку `Web apps` (или коротко `Web`)
10. Нажать кнопку `Reload foodplanlike.pythonanywhere.com`