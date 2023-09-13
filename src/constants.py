from pathlib import Path

BASE_DIR = Path(__file__).parent

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEPS_URL = 'https://peps.python.org/'

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

PRETTY_OUTPUT = 'pretty'
FILE_OUTPUT = 'file'
DEFAULT_OUTPUTS = 'default'

LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'parser.log'
DOWNLOADS_DIR = 'downloads'
BASE_DIR_DOWNLOADS = BASE_DIR / DOWNLOADS_DIR
RESULTS_DIR = 'results'

RESULTS_WHATS_NEWS = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
RESULTS_LATEST_VERSION = [('Ссылка на документацию', 'Версия', 'Статус')]
PARSER_START = 'Парсер запущен!'
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
