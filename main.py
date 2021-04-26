import requests
from pprint import pprint


def get_response(url, **payload):
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


def fetch_hh_vacancies(programming_languages):
    url = 'https://api.hh.ru/vacancies'
    result = {}
    for programming_language in programming_languages[:1]:
        response = get_response(url, area=1, period=30, text=programming_language)
        vacancies = response['items']
        vacancies_found = response['found']
        vacancies_processed = [
            predict_rub_salary(vacancy) for vacancy in vacancies
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
