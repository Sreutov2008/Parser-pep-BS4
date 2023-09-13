import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (BASE_DIR, DATETIME_FORMAT, DEFAULT_OUTPUTS, FILE_OUTPUT,
                       PRETTY_OUTPUT, RESULTS_DIR)

FILE_RESULT = 'Файл с результатами был сохранён: {file_path}'


def default_output(results, *args):
    for row in results:
        print(*row)


def pretty_output(results, *args):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    results_dir = BASE_DIR / RESULTS_DIR
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, csv.unix_dialect)
        writer.writerows(results)
    logging.info(FILE_RESULT.format(file_path=file_path))


OUTPUT_METHODS = {
    PRETTY_OUTPUT: pretty_output,
    FILE_OUTPUT: file_output,
    DEFAULT_OUTPUTS: default_output
}


def control_output(results, cli_args):
    output = 'default'
    if cli_args.output:
        output = cli_args.output

    OUTPUT_METHODS[output](results, cli_args)
