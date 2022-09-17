import logging
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s',
)
logger = logging.getLogger(__name__)


PRACTICUM_TOKEN = os.getenv('PRAC_TOKEN')
TELEGRAM_TOKEN = os.getenv('TG_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TG_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(
            'Отправлено на chat_id:{TELEGRAM_CHAT_ID},сообщениe: {message}'
        )
    except Exception:
        logger.error('Ошибка Отправки сообщения')


def get_api_answer(current_timestamp):
    """делает запрос к единственному эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    homework_statuses = requests.get(
        ENDPOINT, headers=HEADERS, params=params
    )
    if homework_statuses.status_code != HTTPStatus.OK:
        logger.error("API возвращает код, отличный от 200")
        raise Exception("API возвращает код, отличный от 200")
    return homework_statuses.json()


def check_response(response):
    """проверяет ответ API на корректность."""
    if type(response) is not dict:
        raise TypeError('Нет словоря в ответе API')

    try:
        list_homeworks = response['homeworks']
    except KeyError:
        logger.error('homeworks: ошибка словаря')
        raise KeyError('Ошибка словаря по ключу homeworks')

    if type(list_homeworks) is not list:
        raise TypeError('Нет списка в ответе API  ключу homeworks')
    if len(list_homeworks) == 0:
        logging.info('список домашних работ пуст')
    return list_homeworks


def parse_status(homework):
    """извлекает из информации о конкретной домашней работе
    статус этой работы."""
    if 'homework_name' not in homework:
        raise KeyError('Отсутствует ключ "homework_name" в ответе API')
    if 'status' not in homework:
        raise Exception('Отсутствует ключ "status" в ответе API')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        raise Exception(f'Неизвестный статус работы: {homework_status}')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """проверяет доступность переменных окружения"""
    renvironment_variables = {
        'PRACTICUM': PRACTICUM_TOKEN,
        'TELEGRAM': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
    }
    for token in renvironment_variables:
        if not renvironment_variables[token]:
            logger.critical(
                f'Отсутствует token: {token}!')
            return False
    return True


def main():
    """Основная логика работы бота."""
    MASSAGE = ''
    ERROR_MASSAGE = ''
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            logger.info(response)
            current_timestamp = response.get('current_date')
            homework = check_response(response)
            if homework:
                message = parse_status(homework[0])
                if message != MASSAGE:
                    send_message(bot, message)
                MASSAGE = message
            time.sleep(RETRY_TIME)
        except Exception as error:
            message_error = f'Сбой в работе программы: {error}'
            logger.error(error)
            if message_error != ERROR_MASSAGE:
                send_message(bot, message_error)
                ERROR_MASSAGE = message_error
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logger.info("старт модуля")
    main()
