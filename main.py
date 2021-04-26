import requests


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


def main():
    hh_url = 'https://api.hh.ru/vacancies'
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

    api_hh_response = get_response(
        hh_url,
        area=1
    )
    hh_moscow_vacancies_all_count = api_hh_response['found']
    print(f'Количество вакансий за все время: {hh_moscow_vacancies_all_count}')

    for programming_language in programming_languages:
        api_hh_response = get_response(
            hh_url,
            area=1,
            period=30,
            text=programming_language
        )
        hh_moscow_vacancies_month_count = api_hh_response['found']
        print(
            f'Количество вакансий для языка программирования {programming_language} '
            f'за месяц: {hh_moscow_vacancies_month_count}'
        )
        vacancies = api_hh_response['items']
        for vacancy in vacancies:
            print(predict_rub_salary(vacancy))


if __name__ == '__main__':
    main()
