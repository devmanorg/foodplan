# Food Plan Like
Сайт-помощник для выбора еды на неделю.  
[foodplanlike.pythonanywhere.com](http://foodplanlike.pythonanywhere.com/)

# Требования к окружению
- Python 3.8  
Для установки нескольких питонов можно использовать [pyenv](https://github.com/pyenv/pyenv#installation)

# Как запустить локально
- Склонировать репозиторий
- Скачать [медиа](https://drive.google.com/file/d/1au3SNutA19KLfb9tO3izs2oOWyFInT50/view?usp=sharing) в папку media 
- Скачать [базу данных](https://drive.google.com/file/d/16ZwOceKFUSdsT3HbM84CVq4MwCYNXbEA/view?usp=sharing) в корень проекта
- `pip istall -r requirements.txt`
- `export DJANGO_SETTINGS_MODULE='foodplan.settings'`
- `PYTHONPATH=. django-admin migrate`
- `PYTHONPATH=. django-admin collectstatic`
- `PYTHONPATH=. django-admin runserver`