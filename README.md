# Homework_bot

#### **Стек**
![python version](https://img.shields.io/badge/Python-3.7-green)

[python-telegram-bot](https://docs.python-telegram-bot.org/en/stable/)


Бот для Телеграмма работает с Домашкой Яндекс.Практикум, получает обновления проверки последней домашней работы.<br>
Получить PRACTICUM_TOKEN: https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a

## Environment
```bash
PRACTICUM_TOKEN='ваш токен'
TELEGRAM_TOKEN='тг токен'
TELEGRAM_CHAT_ID='токен бота'
```

## Установка Debian
```bash
$ cd /root/
$ mkdir python_projects
$ cd python_projects
$ git clone git@github.com:Not-user-1984/homework_bot.git
$ cd homework_bot
$ python3 -m venv venv
$ source venv/bin/activate
(venv)$ pip install -r requirements.txt
$ nano /etc/environment
$ nano /lib/systemd/system/yaprbot.service
```

```
[Unit]
Description=Yandex.Praktikum Telegram Bot
After=network.target

[Service]
EnvironmentFile=/etc/environment
ExecStart=/root/python_projects/homework_bot/venv/bin/python homework.py
ExecReload=/root/python_projects/homework_bot/venv/bin/python homework.py
WorkingDirectory=/root/python_projects/homework_bot/
KillMode=process
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
$ systemctl enable yaprbot
$ systemctl start yaprbot

$ systemctl status yaprbot  # статус
$ journalctl -u yaprbot.service  # логи
```
### **Разработчик**
[Дима Плужников](https://github.com/Not-user-1984)
