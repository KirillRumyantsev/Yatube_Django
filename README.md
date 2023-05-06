# Сервис Yatube

## Учебный сервис "Yatube" Личные блоги
Сервис микроблогов, на котором можно создать свою страницу, вести свой блог, читать посты других пользователей, подписываться на интересующих авторов и комментировать их посты.
Записи можно отправить в сообщество и посмотреть там записи разных авторов.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git@github.com:KirillRumyantsev/Yatube_Django.git
```

```
cd api_final_yatube
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
