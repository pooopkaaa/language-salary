import os
import argparse
from itertools import count

from dotenv import load_dotenv
import requests
from terminaltables import AsciiTable


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
        return (salary_to + salary_from) // 2
    elif salary_from:
        return salary_from * 1.2
    elif salary_to:
        return salary_to * 0.8


def predict_rub_salary_hh(vacancy):
    raw_salary = vacancy['salary']
    if raw_salary and raw_salary.get('currency') == 'RUR':
        return predict_salary(raw_salary['from'], raw_salary['to'])


def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] == 'rub':
        return predict_salary(vacancy['payment_from'], vacancy['payment_to'])


def get_vacancies_on_page_hh(url, payload):
    for page_number in count():
        payload['page'] = page_number
        response = get_response(url, payload)
        vacancies_found = response['found']
        for vacancy in response['items']:
            yield vacancy, vacancies_found
        if page_number == response['pages'] - 1:
            break


def get_vacancies_on_page_sj(url, header, payload):
    for page_number in count():
        payload['page'] = page_number
        response = get_response(url, payload, header)
        vacancies_found = response['total']
        for vacancy in response['objects']:
            yield vacancy, vacancies_found
        if not response['more']:
            break


def get_processed_salaries_hh(url, payload, programming_language):
    payload['text'] = programming_language
    processed_salaries = []
    for vacancy, vacancies_found in get_vacancies_on_page_hh(url, payload):
        predicted_rub_salary = predict_rub_salary_hh(vacancy)
        if predicted_rub_salary:
            processed_salaries.append(predicted_rub_salary)
    return processed_salaries, vacancies_found


def get_processed_salaries_sj(url, header, payload, programming_language):
    payload['keyword'] = programming_language
    processed_salaries = []
    for vacancy, vacancies_found in get_vacancies_on_page_sj(url, header, payload):
        predicted_rub_salary = predict_rub_salary_sj(vacancy)
        if predicted_rub_salary:
            processed_salaries.append(predicted_rub_salary)
    return processed_salaries, vacancies_found


def fetch_statistics_hh(town_id, period, programming_languages):
    statistics = {}
    url = 'https://api.hh.ru/vacancies'
    payload = {'area': town_id, 'period': period, 'per_page': 100}

    for programming_language in programming_languages[:1]:
        processed_salaries, vacancies_found = get_processed_salaries_hh(
            url,
            payload,
            programming_language
        )
        processed_vacancies_count = len(processed_salaries)
        if processed_vacancies_count:
            average_salary = int(sum(processed_salaries) // processed_vacancies_count)
            statistics[programming_language] = {
                'vacancies_found': vacancies_found,
                'vacancies_processed': processed_vacancies_count,
                'average_salary': average_salary,
            }
    return statistics


def fetch_statistics_sj(town_id, period, programming_languages, api_superjob_secretkey):
    statistics = {}
    url = 'https://api.superjob.ru/2.0/vacancies/'
    header = {'X-Api-App-Id': api_superjob_secretkey}
    payload = {'town': town_id, 'period': period, 'count': 100}

    for programming_language in programming_languages[:1]:
        processed_salaries, vacancies_found = get_processed_salaries_sj(
            url,
            header,
            payload,
            programming_language
        )
        processed_vacancies_count = len(processed_salaries)
        if processed_vacancies_count:
            average_salary = int(sum(processed_salaries) // processed_vacancies_count)
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
            programming_language,
            statistic['vacancies_found'],
            statistic['vacancies_processed'],
            statistic['average_salary'],
        ]
        for programming_language, statistic in statistics.items()
    ]
    table.insert(0, table_first_line)
    table_instance = AsciiTable(table, title)
    return table_instance.table


def main():
    load_dotenv()
    api_superjob_secretkey = os.environ.get('API_SUPERJOB_SECRETKEY')
    programming_languages = [
        'Python', 'JavaScript', 'Java',
        'Ruby', 'PHP', 'C++', 'C#',
        'Swift', 'Go', 'Objective-C',
    ]
    command_line_args = get_command_line_args()
    town = command_line_args.town
    period = command_line_args.period

    try:
        sj_town_id, hh_town_id = get_town_id_sj(town), get_town_id_hh(town)

        sj_statistics = fetch_statistics_sj(
            sj_town_id,
            period,
            programming_languages,
            api_superjob_secretkey
        )
        if sj_statistics:
            sj_title = f'SuperJob {town}'
            print(get_terminal_table(sj_statistics, sj_title))

        hh_statistics = fetch_statistics_hh(hh_town_id, period, programming_languages)
        if hh_statistics:
            hh_title = f'HeadHunter {town}'
            print(get_terminal_table(hh_statistics, hh_title))
    except requests.exceptions.HTTPError as http_error:
        print(http_error)


if __name__ == '__main__':
    main()
