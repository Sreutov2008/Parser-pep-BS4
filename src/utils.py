from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserFindTagException

ERROR = 'Произошла ошибка: {e}'
ERROR_TAG = 'Не найден тег {tag} {attrs}'
ERROR_URL = 'Не найден url {url}'
GET_RESPONSE_ERROR = 'Возникла ошибка при загрузке страницы {url}'


def get_response(session, url, encoding='utf-8'):
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException as e:
        raise ConnectionError(
            GET_RESPONSE_ERROR.format(url=url, error=str(e))
        )


def get_soup(session, url, features="lxml"):
    return BeautifulSoup(
        get_response(session, url).text,
        features=features
    )


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        raise ParserFindTagException(ERROR_TAG.format(tag=tag, attrs=attrs))
    return searched_tag


class DelayedLogger:
    def __init__(self):
        self.__messages = []

    def add_message(self, message):
        self.__messages.append(message)

    def log(self, logger):
        for error_message in self.__messages:
            logger(error_message)
