import logging
import os
from http import HTTPStatus
from json.decoder import JSONDecodeError
from time import sleep, time

import requests
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

import exceptions
import endpoint

load_dotenv()


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s',
)
logger = logging.getLogger(__name__)


PRACTICUM_TOKEN = os.getenv('PRAC_TOKEN')
TELEGRAM_TOKEN = os.getenv('TG_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TG_CHAT_ID')
TELEGRAM_RETRY_TIME = 600

HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICT = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(
            f'Отправлено на chat_id:{TELEGRAM_CHAT_ID},сообщениe: {message}'
        )
    except TelegramError:
        logger.error('Ошибка Отправки сообщения')


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    homework_statuses = requests.get(
        endpoint.PRACTICUM_ENDPOINT, headers=HEADERS, params=params
    )
    if homework_statuses.status_code != HTTPStatus.OK:
        logger.error("API возвращает код, отличный от 200")
        raise exceptions.APIUnexpectedHTTPStatus(
            "API возвращает код, отличный от 200"
        )
    try:
        json_homework = homework_statuses.json()
    except JSONDecodeError:
        logger.error("ответ не преобразуется в json")
    return json_homework


def check_response(response):
    """Проверяет ответ API на корректность."""
    logger.info("началo проверки ответа сервера")
    if type(response) is not dict:
        raise TypeError('Нет словоря в ответе API')

    try:
        list_homeworks = response['homeworks']
    except exceptions.CheckResponseException:
        logger.error('homeworks: ошибка словаря')
        raise KeyError('Ошибка словаря по ключу homeworks')

    if type(list_homeworks) is not list:
        raise exceptions.CheckResponseException(
            'Нет списка в ответе API  ключу homeworks'
        )
    return list_homeworks


def parse_status(homework):
    """Парсер статус этой работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if homework_name is None:
        raise KeyError('Отсутствует ключ "homework_name" в ответе API')
    if homework_status is None:
        raise exceptions.ParseStatusException(
            'Отсутствует ключ "status" в ответе API'
        )

    if homework_status not in HOMEWORK_VERDICT:
        raise exceptions.ParseStatusException(
            f'Неизвестный статус работы: {homework_status}'
        )

    verdict = HOMEWORK_VERDICT.get(homework_status)
    if verdict is None:
        raise exceptions.NonStatusException(
            "нет такого статуса, возможно нужно обновить HOMEWORK_VERDICT "
        )

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_TOKEN]):
        return True
    # return PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Нет переменных окружения')
        raise exceptions.NoTokensException('Нет переменных окружения')
    MASSAGE = ''
    ERROR_MASSAGE = ''
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time())
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
            else:
                logging.info('список домашних работ пуст')
        except Exception as error:
            message_error = f'Сбой в работе программы: {error}'
            logger.error(error)
            if message_error != ERROR_MASSAGE:
                send_message(bot, message_error)
                ERROR_MASSAGE = message_error
        finally:
            sleep(TELEGRAM_RETRY_TIME)


if __name__ == '__main__':
    logger.info("старт модуля")
    main()

