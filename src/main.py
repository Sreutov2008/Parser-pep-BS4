from constants import BASE_DIR, MAIN_DOC_URL, PEPS_URL, EXPECTED_STATUS
import requests_cache
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm
import re
from configs import configure_argument_parser, configure_logging
from outputs import control_output
import logging
from utils import get_response, find_tag


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return None
    soup = BeautifulSoup(response.text, features='lxml')

    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all('li', attrs={'class': 'toctree-l1'})

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        version_link = urljoin(whats_new_url, version_a_tag['href'])
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )

    return results


def latest_versions(session):
    # session = requests_cache.CachedSession()
    #response = session.get(MAIN_DOC_URL)
    #response.encoding = 'utf-8'
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    # Создание "супа".
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        # Проверка, есть ли искомый текст в содержимом тега.
        if 'All versions' in ul.text:
            # Если текст найден, ищутся все теги <a> в этом списке.
            a_tags = ul.find_all('a')
            # Остановка перебора списков.
            break
    # Если нужный список не нашёлся,
    # вызывается исключение и выполнение программы прерывается.
    else:
        raise Exception('Ничего не нашлось')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    # Шаблон для поиска версии и статуса:
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    # Цикл для перебора тегов <a>, полученных ранее.
    for a_tag in a_tags:
        # Напишите новый код, ориентируясь на план.
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            # Если строка соответствует паттерну,
            # переменным присываивается содержимое групп, начиная с первой.
            version, status = text_match.groups()
        else:
            # Если строка не соответствует паттерну,
            # первой переменной присваивается весь текст, второй — пустая строка.
            version, status = a_tag.text, ''
            # Добавление полученных переменных в список в виде кортежа.
        results.append(
            (link, version, status)
        )
        # Печать результата.
    #for row in results:
    #    print(*row)
    return results


def download(session):
    # Вместо константы DOWNLOADS_URL, используйте переменную downloads_url.
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    # Загрузка веб-страницы с кешированием.
    # session = requests_cache.CachedSession()
    #response = session.get(downloads_url)
    #response.encoding = 'utf-8'
    response = get_response(session, downloads_url)
    if response is None:
        return
    # Создание "супа".
    soup = BeautifulSoup(response.text, features='lxml')
    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')})

    # Сохраните в переменную содержимое атрибута href.
    pdf_a4_link = pdf_a4_tag['href']
    # Получите полную ссылку с помощью функции urljoin.
    archive_url = urljoin(downloads_url, pdf_a4_link)
    print(archive_url)
    filename = archive_url.split('/')[-1]
    # Сформируйте путь до директории downloads.
    downloads_dir = BASE_DIR / 'downloads'
    # Создайте директорию.
    downloads_dir.mkdir(exist_ok=True)
    # Получите путь до архива, объединив имя файла с директорией.
    archive_path = downloads_dir / filename

    # Загрузка архива по ссылке.
    response = session.get(archive_url)

    # В бинарном режиме открывается файл на запись по указанному пути.
    with open(archive_path, 'wb') as file:
        # Полученный ответ записывается в файл.
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    response = get_response(session, PEPS_URL)
    if response is None:
        return
    # Создание "супа".
    soup = BeautifulSoup(response.text, features='lxml')
    pep_table = find_tag(soup, 'section', {'id': 'numerical-index'})
    pep_table_data = find_tag(pep_table, 'tbody')
    pep_tags = pep_table_data.find_all('tr')
    errors = []
    pep_list = []
    statuses = []
    result = [("Статус", "Количество")]
    for pep_tag in tqdm(pep_tags):
        preview_status = find_tag(pep_tag, 'abbr').text[1:]
        href = find_tag(pep_tag, 'a')['href']
        pep_link = urljoin(PEPS_URL, href)
        response = get_response(session, pep_link)
        if response is None:
            continue

        soup = BeautifulSoup(response.text, features='lxml')
        description = find_tag(soup, 'dl',  attrs={'class': 'rfc2822 field-list simple'})
        status_element = description.find(string="Status")
        status = status_element.find_parent().find_next_sibling().text
        pep_list.append(status)

        try:
            if status not in EXPECTED_STATUS[preview_status]:
                errors.append((pep_link, preview_status, status))

        except KeyError:
            logging.error('Неизвестный статус:' f'{preview_status}')

    for status_list in EXPECTED_STATUS.values():
        for status in status_list:
            if status not in statuses:
                statuses.append(status)
                result.append((status, pep_list.count(status)))

    result.append(("Total", len(pep_list)))
        #print(pep_list)
    return result




# Скопируйте весь код ниже.
MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    # Запускаем функцию с конфигурацией логов.
    configure_logging()
    # Отмечаем в логах момент запуска программы.
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    # Логируем переданные аргументы командной строки.
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)
    # Логируем завершение работы парсера.
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
