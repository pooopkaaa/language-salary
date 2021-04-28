import requests
from pprint import pprint
from itertools import count
import argparse


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


def get_town_ids(town):
    sj_town_id = get_response(f'https://api.superjob.ru/2.0/towns/?keyword={town}')[0]['id']
    
    hh_region_ids = get_response('https://api.hh.ru/areas/113')['areas']
    hh_town_ids = [town['areas'] for town in hh_region_ids]
    print(hh_town_ids)

def get_response(url, payload=None, header=None):
    response = requests.get(url, headers=header, params=payload)
    response.raise_for_status()
    return response.json()


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
            return predict_salary(raw_salary.get('from'), raw_salary.get('to'))


def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] == 'rub':
        return predict_salary(vacancy['payment_from'], vacancy['payment_to'])


def generator_vacancies_for_hh(url, pages, payload):
    for page in range(pages):
        response = get_response(url, payload)
        yield from response['items']


def fetch_vacancies_hh(programming_languages):
    url = 'https://api.hh.ru/vacancies'
    result = {}
    payload = {'area': 1, 'period': 30, 'per_page': 100}

    for programming_language in programming_languages:
        payload['text'] = programming_language
        response = get_response(url, payload)
        vacancies_found = response['found']
        vacancies_pages = response['pages']
        vacancies_processed = [
            predict_rub_salary_hh(vacancy)
            for vacancy in generator_vacancies_for_programming_language(
                url,
                vacancies_pages,
                payload
            )
            if predict_rub_salary_hh(vacancy)
        ]
        vacancies_processed_count = len(vacancies_processed)
        average_salary = int(sum(vacancies_processed)/vacancies_processed_count)

        result[programming_language] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed_count,
            'average_salary': average_salary,
        }
    return result


def generator_vacancies_for_sj(url, header, payload):
    for page in count():
        payload['page'] = page
        response = get_response(url, header=header, payload=payload)
        yield from response['objects']
        if not response['more']:
            break


def fetch_statistics_sj(programming_languages, town, period):
    result = {}
    url = 'https://api.superjob.ru/2.0/vacancies/'
    header = {
        'X-Api-App-Id': 'v3.r.134199680.69d2207fa683ebb1ca84016dacc5e518baea99a0.515c5e943980a1855a590cd4a7023dd82e290d8a',
    }
    town_id = get_town_id(town)
    payload = {'town': town_id, 'period': period, 'count': 100}
    for programming_language in programming_languages:
        payload['keyword'] = programming_language
        response = get_response(url, header=header, payload=payload)
        vacancies_found = response['total']
        vacancies_processed = [
            predict_rub_salary_sj(vacancy)
            for vacancy in generator_vacancies_for_sj(url, header, payload)
            if predict_rub_salary_sj(vacancy)
        ]
        vacancies_processed_count = len(vacancies_processed)
        average_salary = int(sum(vacancies_processed)//vacancies_processed_count)
        result[programming_language] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed_count,
            'average_salary': average_salary,
        }
    return result


def get_terminal_table(statistics, title):
    table_first_line = ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']
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
    print()


def main():
    programming_languages = [
        'Python',
        'JavaScript',
        'Java',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        'Swift',
        'Go',
        'Objective-C',
    ]

    command_line_args = get_command_line_args()
    town = command_line_args.town
    period = command_line_args.period
    sj_town_id, hh_town_id = get_town_ids(town)

    # sj_statistics = fetch_statistics_sj(programming_languages, sj_town_id, period)
    # sj_title = 'SuperJob {town}'
    # get_terminal_table(sj_statistics, sj_title)

    # hh_statistics = fetch_statistics_hh(programming_languages)
    # hh_title = 'SuperJob {town}'
    # get_terminal_table(hh_statistics, hh_title)


if __name__ == '__main__':
    main()
