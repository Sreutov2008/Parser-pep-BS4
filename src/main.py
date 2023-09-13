import logging
import re
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, DOWNLOADS_DIR, EXPECTED_STATUS, MAIN_DOC_URL,
                       PEPS_URL, RESULTS_LATEST_VERSION, RESULTS_WHATS_NEWS)
from outputs import control_output
from utils import GET_RESPONSE_ERROR, DelayedLogger, find_tag, get_soup

ANEXPECTED_STATUS = 'Неизвестный статус: {preview_status}'
ARCHIVE_PATH = 'Архив был загружен и сохранён: {archive_path}'
COMMAND_ARGUMENTS = 'Аргументы командной строки: {args}'
PARSER_FINISH = 'Парсер завершил работу.'
PARSER_START = 'Парсер запущен!'
ERROR = 'Произошла ошибка: {e}'
NONE_ALL_VERSION = 'Не удалось найти ссылки a с текстом "All versions"'
FILE_RESULT = 'Файл с результатами был сохранён: {file_path}'
ERROR_TAG = 'Не найден тег {tag} {attrs}'


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = get_soup(session, whats_new_url)
    sections_by_python = soup.select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1 > a'
    )
    results = RESULTS_WHATS_NEWS
    delayed_logger = DelayedLogger()
    for section in tqdm(sections_by_python):
        version_link = urljoin(whats_new_url, section['href'])
        try:
            soup = get_soup(session, version_link)
        except ConnectionError:
            DelayedLogger.add_message(GET_RESPONSE_ERROR.format(url=version_link))
            continue
        results.append(
            (version_link,
             find_tag(soup, 'h1').text,
             find_tag(soup, 'dl').text.replace('\n', ' ')
             )
        )
    delayed_logger.log(logging.warning)
    return results


def latest_versions(session):
    soup = get_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise RuntimeError(NONE_ALL_VERSION)

    results = RESULTS_LATEST_VERSION
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (a_tag['href'], version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = get_soup(session, downloads_url)
    pdf_a4_link = soup.select_one(
        'div[role="main"] table.docutils a[href$="pdf-a4.zip"]')['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    result_dir = BASE_DIR / DOWNLOADS_DIR
    result_dir.mkdir(exist_ok=True)
    archive_path = result_dir / filename
    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(ARCHIVE_PATH.format(archive_path=archive_path))


def pep(session):
    delayed_logger = DelayedLogger()
    soup = get_soup(session, PEPS_URL)
    pep_tags = soup.select('#numerical-index tbody tr')
    pep_list = []

    for pep_tag in tqdm(pep_tags):
        preview_status = find_tag(pep_tag, 'abbr').text[1:]
        href = find_tag(pep_tag, 'a')['href']
        pep_link = urljoin(PEPS_URL, href)
        try:
            soup = get_soup(session, pep_link)
        except ConnectionError:
            delayed_logger.add_message(GET_RESPONSE_ERROR.format(url=pep_link))
            continue
        status = soup.find('dl', class_='rfc2822 field-list simple').find(
            string="Status").find_parent().find_next_sibling().text
        pep_list.append(status)

        try:
            if status not in EXPECTED_STATUS[preview_status]:
                delayed_logger.add_message((pep_link, preview_status, status))

        except KeyError:
            delayed_logger.add_message(
                ANEXPECTED_STATUS.format(preview_status=preview_status)
            )
            continue
    delayed_logger.log(logging.warning)
    return [
        ('Статус', 'Количество'),
        *[
            (status, pep_list.count(status))
            for status_list in EXPECTED_STATUS.values()
            for status in status_list
        ],
        ('Всего', len(pep_list))
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info(PARSER_START)
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(COMMAND_ARGUMENTS.format(args=args))

    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()

        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)

        if results is not None:
            control_output(results, args)
        logging.info(PARSER_FINISH)
    except Exception as e:
        logging.info(ERROR.format(e=e))


if __name__ == '__main__':
    main()
