import requests


def response(url, **payload):
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.json()


def main():
    hh_url = 'https://api.hh.ru/vacancies'
    api_hh_response = response(hh_url, area=1)
    hh_moscow_vacancies_all_count = api_hh_response['found']
    print(f'Количество вакансий за все время: {hh_moscow_vacancies_all_count}')

    api_hh_response = response(hh_url, area=1, period=30)
    hh_moscow_vacancies_month_count = api_hh_response['found']
    print(f'Количество вакансий за месяц: {hh_moscow_vacancies_month_count}')


if __name__ == '__main__':
    main()