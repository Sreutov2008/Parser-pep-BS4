import logging

from bs4 import BeautifulSoup

from constants import ERROR, ERROR_TAG
from exceptions import ParserFindTagException, ParserUrlException


def get_response(session, url, encoding='utf-8'):
    response = session.get(url)
    response.encoding = encoding
    response.raise_for_status()
    return response


def get_soup(session, url):
    try:
        response = get_response(session, url)
        if response is None:
            return
    except ParserUrlException:
        logging.error(ERROR.format(e=url))
    soup = BeautifulSoup(response.text, features="lxml")

    return soup


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_message = ERROR_TAG.format(tag=tag, attrs=attrs)
        logging.error(error_message, stack_info=True)
        raise ParserFindTagException(error_message)
    return searched_tag
