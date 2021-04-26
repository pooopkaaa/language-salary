import requests


def get_response(url, **payload):
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.json()


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
            f'Количество вакансий для языка программирования {programming_language}'
            f'за месяц: {hh_moscow_vacancies_month_count}'
        )
        vacancies = api_hh_response['items']
        for vacancy in vacancies:
            print(vacancy['salary'])



if __name__ == '__main__':
    main()
