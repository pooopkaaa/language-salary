import os
import argparse
from itertools import count

from dotenv import load_dotenv
import requests
from terminaltables import AsciiTable


load_dotenv()
API_SUPERJOB_SECRETKEY = os.environ.get('API_SUPERJOB_SECRETKEY')
PROGRAMMING_LANGUAGES = [
    'Python', 'JavaScript', 'Java',
    'Ruby', 'PHP', 'C++', 'C#',
    'Swift', 'Go', 'Objective-C',
]


def get_command_line_args():
    parser = argparse.ArgumentParser(
        description='Скрипт для поиска размера зарплаты\
        среди популярных языков программирования'
    )
    parser.add_argument(
        '-t',
        '--town',
        default='Москва',
        type=str,
        help='Укажите город для поиска вакансий'
    )
    parser.add_argument(
        '-p',
        '--period',
        default=30,
        type=int,
        help='Укажите за какой промежуток дней предоставить статистику'
    )
    return parser.parse_args()


def get_response(url, payload=None, header=None):
    response = requests.get(url, headers=header, params=payload)
    response.raise_for_status()
    return response.json()


def get_town_id_sj(town):
    url = 'https://api.superjob.ru/2.0/towns'
    payload = {'keyword': town}
    return get_response(url, payload)['objects'][0]['id']


def get_town_id_hh(town):
    url = 'https://api.hh.ru/suggests/area_leaves'
    payload = {'text': town}
    return get_response(url, payload)['items'][0]['id']


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_to + salary_from)//2
    elif salary_from:
        return salary_from*1.2
    elif salary_to:
        return salary_to*0.8


def predict_rub_salary_hh(vacancy):
    raw_salary = vacancy['salary']
    if raw_salary:
        if raw_salary.get('currency') == 'RUR':
            return predict_salary(raw_salary['from'], raw_salary['to'])


def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] == 'rub':
        return predict_salary(vacancy['payment_from'], vacancy['payment_to'])


def generator_vacancies_for_hh(url, pages_amount, payload):
    for page_number in range(pages_amount):
        response = get_response(url, payload)
        yield from response['items']


def generator_vacancies_for_sj(url, header, payload):
    for page_number in count():
        payload['page'] = page_number
        response = get_response(url, payload, header)
        yield from response['objects']
        if not response['more']:
            break


def fetch_statistics_hh(town_id, period):
    statistics = {}
    url = 'https://api.hh.ru/vacancies'
    payload = {'area': town_id, 'period': period, 'per_page': 100}

    for programming_language in PROGRAMMING_LANGUAGES[:1]:
        payload['text'] = programming_language
        response = get_response(url, payload)
        vacancies_found = response['found']
        vacancies_pages_amount = response['pages']
        processed_salaries = []
        for vacancy in generator_vacancies_for_hh(url, vacancies_pages_amount, payload):
            predicted_rub_salary = predict_rub_salary_hh(vacancy)
            if predicted_rub_salary:
                processed_salaries.append(predicted_rub_salary)
        processed_vacancies_count = len(processed_salaries)
        if processed_vacancies_count:
            average_salary = int(sum(processed_salaries)/processed_vacancies_count)
            statistics[programming_language] = {
                'vacancies_found': vacancies_found,
                'vacancies_processed': processed_vacancies_count,
                'average_salary': average_salary,
            }
    return statistics


def fetch_statistics_sj(town_id, period):
    statistics = {}
    url = 'https://api.superjob.ru/2.0/vacancies/'
    header = {'X-Api-App-Id': API_SUPERJOB_SECRETKEY}
    payload = {'town': town_id, 'period': period, 'count': 100}

    for programming_language in PROGRAMMING_LANGUAGES[:1]:
        payload['keyword'] = programming_language
        response = get_response(url, payload, header)
        vacancies_found = response['total']
        processed_salaries = []
        for vacancy in generator_vacancies_for_sj(url, header, payload):
            predicted_rub_salary = predict_rub_salary_sj(vacancy)
            if predicted_rub_salary:
                processed_salaries.append(predicted_rub_salary)
        processed_vacancies_count = len(processed_salaries)
        if processed_vacancies_count:
            average_salary = int(sum(processed_salaries)//processed_vacancies_count)
            statistics[programming_language] = {
                'vacancies_found': vacancies_found,
                'vacancies_processed': processed_vacancies_count,
                'average_salary': average_salary,
            }
    return statistics


def get_terminal_table(statistics, title):
    table_first_line = [
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата'
    ]
    table = [
        [
            language_static,
            statistics[language_static]['vacancies_found'],
            statistics[language_static]['vacancies_processed'],
            statistics[language_static]['average_salary']
        ]
        for language_static in statistics
    ]
    table.insert(0, table_first_line)
    table_instance = AsciiTable(table, title)
    print(table_instance.table)


def main():
    command_line_args = get_command_line_args()
    town = command_line_args.town
    period = command_line_args.period

    try:
        sj_town_id, hh_town_id = get_town_id_sj(town), get_town_id_hh(town)

        sj_statistics = fetch_statistics_sj(sj_town_id, period)
        if sj_statistics:
            sj_title = f'SuperJob {town}'
            get_terminal_table(sj_statistics, sj_title)

        hh_statistics = fetch_statistics_hh(hh_town_id, period)
        if hh_statistics:
            hh_title = f'HeadHunter {town}'
            get_terminal_table(hh_statistics, hh_title)
    except requests.exceptions.HTTPError as http_error:
        print(http_error)


if __name__ == '__main__':
    main()
