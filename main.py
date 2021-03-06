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
    return (salary_from + salary_to) / 2


def calculate_hh_salaries(vacancies):
    salaries = []
    for vacancy in vacancies:
        if not vacancy['salary'] or vacancy['salary']['currency'] != 'RUR':
            salaries.append(None)
            continue
        salary_from = vacancy['salary']['from']
        salary_to = vacancy['salary']['to']
        salaries.append(predict_salary(salary_from, salary_to))
    return salaries


def get_hh_salaries(url, programming_language):
    programmer_id = 1.221
    moscow_id = 1
    payload = {
        'specialization': programmer_id,
        'area': moscow_id,
        'text': programming_language,
    }
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
    specialist_salaries = {}
    for programming_language in specializations:
        vacancies_number, salaries = get_hh_salaries(url, programming_language)
        filtered_salaries = [float(salary) for salary in salaries if salary]
        specialist_salaries[programming_language] = {
            'vacancies_found': vacancies_number,
            'vacancies_processed': len(filtered_salaries),
            'average_salary': int(np.mean(filtered_salaries)),
        }
    return specialist_salaries


def calculate_sj_salaries(vacancies):
    salaries = []
    for vacancy in vacancies:
        salary_from = vacancy['payment_from']
        salary_to = vacancy['payment_to']
        salaries.append(predict_salary(salary_from, salary_to))
    return salaries


def get_sj_salaries(url, headers, programming_language):
    search_by_post = 1
    per_page_vacancies_number = 20
    payload = {
        'count': per_page_vacancies_number,
        'keyword': programming_language,
        'keywors': {
            'srws': search_by_post,
            'skwc': 'or',
            'key': '??????????????????????',
        },
        'town': '????????????',
    }
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
    specialist_salaries = {}
    for programming_language in specializations:
        salaries, vacancies_number = get_sj_salaries(url, headers,
                                                     programming_language)
        filtered_salaries = [float(salary) for salary in salaries if salary]
        specialist_salaries[programming_language] = {
            'vacancies_found': vacancies_number,
            'vacancies_processed': len(filtered_salaries),
            'average_salary': int(np.mean(filtered_salaries)),
        }
    return specialist_salaries


def create_table(specialist_salaries, table_title):
    table_data = [
        [
            '???????? ????????????????????????????????',
            '???????????????? ??????????????',
            '???????????????? ????????????????????',
            '?????????????? ????????????????'
        ]
    ]
    for programming_language, search_results in specialist_salaries.items():
        table_data.append([programming_language]
                          + list(search_results.values()))
    table = AsciiTable(table_data)
    table.title = table_title
    salaries_table = table.table
    return salaries_table


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
    hh_salaries_table = create_table(hh_programmer_salaries, hh_table_title)
    print(hh_salaries_table)
    sj_salaries_table = create_table(sj_programmer_salaries, sj_table_title)
    print(sj_salaries_table)
