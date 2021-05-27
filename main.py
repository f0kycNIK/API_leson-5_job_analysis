import os

import numpy as np
import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


def predict_salary(salary_from, salary_to):
    if not salary_from and not salary_to:
        return None
    elif salary_from and not salary_to:
        return salary_from * 1.2
    elif not salary_from and salary_to:
        return salary_to * 0.9
    else:
        return (salary_from + salary_to) / 2


def calculate_hh_salaries(vacancies):
    salaries = []
    for vacancy in vacancies:
        if not vacancy['salary'] or vacancy['salary']['currency'] != 'RUR':
            salaries.append(None)
        else:
            salary_from = vacancy['salary']['from']
            salary_to = vacancy['salary']['to']
            salaries.append(predict_salary(salary_from, salary_to))
    return salaries


def get_hh_salaries(url, payload):
    salaries = []
    pages_number = 1
    page = 0
    while page < pages_number:
        payload['page'] = page
        response = requests.get(url, params=payload)
        response.raise_for_status()
        searching_results = response.json()
        vacancies = searching_results['items']
        vacancies_number = searching_results['found']
        salaries += calculate_hh_salaries(vacancies)
        pages_number = searching_results['pages']
        page += 1
    return vacancies_number, salaries


def predict_rub_salary_hh(url, specializations):
    payload = {
        'specialization': 1.221,
        'area': 1,
        'text': [],
        'page': [],
    }
    specialist_salaries = {}
    for name in specializations:
        payload['text'] = name
        vacancies_number, salaries = get_hh_salaries(url, payload)
        sorted_salaries = [float(salary) for salary in salaries if salary]
        specialist_salaries.update(
            {
                name: {
                    'vacabcies_found': str(vacancies_number),
                    'vacancies_processed': str(len(sorted_salaries)),
                    'average_salary': str(int(np.mean(sorted_salaries))),
                }
            }
        )
    return specialist_salaries


def calculate_sj_salaries(vacancies):
    salaries = []
    for vacancy in vacancies:
        salary_from = vacancy['payment_from']
        salary_to = vacancy['payment_to']
        salaries.append(predict_salary(salary_from, salary_to))
    return salaries


def get_sj_salaries(url, headers, payload):
    additional_vacancies = True
    page_number = 0
    salaries = []
    while additional_vacancies:
        payload['page'] = page_number
        response = requests.get(url, headers=headers, params=payload)
        response.raise_for_status()
        vacancies = response.json()
        salaries += calculate_sj_salaries(vacancies['objects'])
        additional_vacancies = vacancies['more']
        vacancies_number = vacancies['total']
        page_number += 1
    return salaries, vacancies_number


def predict_rub_salary_sj(url, headers, specializations):
    payload = {
        'page': [],
        'count': 20,
        'keyword': [],
        'keywors': {
            'srws': 1,
            'skwc': 'or',
            'key': 'Программист',
        },
        'town': 'Москва',
    }
    specialist_salaries = {}
    for name in specializations:
        payload['keyword'] = name
        salaries, vacancies_number = get_sj_salaries(url, headers, payload)
        sorted_salaries = [float(var) for var in salaries if var]
        specialist_salaries.update(
            {name: {
                'vacabcies_found': str(vacancies_number),
                'vacancies_processed': str(len(sorted_salaries)),
                'average_salary': str(int(np.mean(sorted_salaries))),
            }
            }
        )
    return specialist_salaries


def create_table(specialist_salaries, table_title):
    table_data = [
        [
            'Язык программирования',
            'Вакансий найдено',
            'Вакансий обработано',
            'Средняя зарплата'
        ]
    ]
    for key, value in specialist_salaries.items():
        table_data.append(key.split() + list(value.values()))
    table = AsciiTable(table_data)
    table.title = table_title
    print(table.table)


if __name__ == '__main__':
    load_dotenv()

    sj_token = os.getenv('SJ_TOKEN')

    specializations = [
        'Python',
        'JavaScript',
        'Java',
        'Ruby',
        'PHP',
        'C++',
        'CSS',
        'C#',
    ]

    hh_url = 'https://api.hh.ru/vacancies'

    sj_url = 'https://api.superjob.ru/2.0/vacancies'
    sj_headers = {
        'X-Api-App-Id': sj_token
    }

    hh_table_title = 'HeadHunter Moscow'
    sj_table_title = 'SuperJob Moscow'

    hh_programmer_salaries = predict_rub_salary_hh(hh_url, specializations)
    sj_programmer_salaries = predict_rub_salary_sj(sj_url, sj_headers,
                                                   specializations)

    create_table(hh_programmer_salaries, hh_table_title)
    create_table(sj_programmer_salaries, sj_table_title)
