import requests
from pprint import pprint
from itertools import count


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
    

def generator_vacancies_for_programming_language(url, pages, payload):
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
            for vacancy in generator_vacancies_for_programming_language(url, vacancies_pages, payload)
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


def fetch_vacancies_sj(programming_languages):
    result = {}
    url = 'https://api.superjob.ru/2.0/vacancies/'
    header = {
        'X-Api-App-Id': 'v3.r.134199680.69d2207fa683ebb1ca84016dacc5e518baea99a0.515c5e943980a1855a590cd4a7023dd82e290d8a',
    }
    payload = {'town': 4, 'period': 0, 'count':100, 'page':1}
    for programming_language in programming_languages[:1]:
        payload['keyword'] = programming_language
        response = get_response(url, header=header, payload=payload)
        pprint(response)
        vacancies_found = response['total']

        for vacancy in response['objects']:
            print(vacancy['profession'], vacancy['town']['title'], predict_rub_salary_sj(vacancy), vacancy['currency'], vacancy['payment_from'], vacancy['payment_to'])


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
    # pprint(fetch_vacancies_hh(programming_languages))
    fetch_vacancies_sj(programming_languages)


if __name__ == '__main__':
    main()
