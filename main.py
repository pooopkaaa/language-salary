import requests
from pprint import pprint
from itertools import count


def get_response(url, payload):
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.json()


def predict_rub_salary(vacancy):
    raw_salary = vacancy['salary']
    if raw_salary:
        if raw_salary.get('currency') == 'RUR':
            from_salary = raw_salary.get('from')
            to_salary = raw_salary.get('to')
            if from_salary and to_salary:
                return (int(to_salary) + int(from_salary))//2
            elif from_salary is None:
                return int(to_salary)*0.8
            elif to_salary is None:
                return int(from_salary)*1.2


def fetch_vacancies_for_programming_language(url, pages, payload):
    for page in range(pages):
        response = get_response(url, payload)
        yield from response['items']


def fetch_hh_vacancies(programming_languages):
    url = 'https://api.hh.ru/vacancies'
    result = {}
    payload = {'area': 1, 'period': 30, 'per_page': 100}

    for programming_language in programming_languages:
        payload['text'] = programming_language
        response = get_response(url, payload)
        vacancies_found = response['found']
        vacancies_pages = response['pages']
        vacancies_processed = [
            predict_rub_salary(vacancy)
            for vacancy in fetch_vacancies_for_programming_language(url, vacancies_pages, payload)
            if predict_rub_salary(vacancy)
        ]
        vacancies_processed_count = len(vacancies_processed)
        average_salary = int(sum(vacancies_processed)/vacancies_processed_count)

        result[programming_language] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed_count,
            'average_salary': average_salary,
        }
    return result


def main():
    programming_languages = [
        'Python',
        'JavaScript',
        'Java',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        'C',
        'Go',
        'Objective-C',
    ]
    pprint(fetch_hh_vacancies(programming_languages))


if __name__ == '__main__':
    main()
