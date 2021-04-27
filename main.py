import requests
from pprint import pprint
from itertools import count


def get_response(url, payload=None, header=None):
    response = requests.get(url, headers=header, params=payload)
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


def fetch_superjob_vacancies(programming_languages):
    secret_key = 'v3.r.134199680.69d2207fa683ebb1ca84016dacc5e518baea99a0.515c5e943980a1855a590cd4a7023dd82e290d8a'
    access_id = '1665'
    url = 'https://api.superjob.ru/2.0/vacancies/'
    header = {
        'X-Api-App-Id': 'v3.r.134199680.69d2207fa683ebb1ca84016dacc5e518baea99a0.515c5e943980a1855a590cd4a7023dd82e290d8a',
    }
    payload = {
        'town': 4,
        'keyword': 'Программист'
    }
    response = get_response(url, header=header, payload=payload)
    for vacancy in response['objects']:
        print(vacancy['profession'], vacancy['town']['title'])


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
    # pprint(fetch_hh_vacancies(programming_languages))
    fetch_superjob_vacancies(programming_languages)


if __name__ == '__main__':
    main()
