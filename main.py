import os

import numpy as np
import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


def predict_salary(salary_from, salary_to):
    condition = [0, None]
    if salary_from in condition and salary_to in condition:
        salary = None
    elif salary_from != None and salary_to in condition:
        salary = salary_from * 1.2
    elif salary_from in condition and salary_to != None:
        salary = salary_to * 0.9
    else:
        salary = (salary_from + salary_to) / 2
    return salary


def calculating_hh_salaries(vacancies):
    salaries = []
    for vacancy in vacancies:
        if vacancy['salary'] == None or vacancy['salary']['currency'] != 'RUR':
            salaries.append(None)
        else:
            salary_from = vacancy['salary']['from']
            salary_to = vacancy['salary']['to']
            salaries.append(predict_salary(salary_from, salary_to))
    return salaries


def getting_hh_salaries(url, payload):
    salaries = []
    pages_number = 1
    page = 0
    while page < pages_number:
        payload['page'] = page
        response = requests.get(url, params=payload)
        response.raise_for_status()
        vacancies = response.json()['items']
        vacancies_number = response.json()['found']
        salaries += calculating_hh_salaries(vacancies)
        pages_number = response.json()['pages']
        page += 1
    return vacancies_number, salaries


def predict_rub_salary_hh(url, payload, list):
    dic = {}
    for name in list:
        payload['text'] = name
        vacancies_number, salaries = getting_hh_salaries(url, payload)
        sorted_salaries = [float(var) for var in salaries if var != None]
        dic.update(
            {
                name: {
                    'vacabcies_found': str(vacancies_number),
                    'vacancies_processed': str(len(sorted_salaries)),
                    'average_salary': str(int(np.mean(sorted_salaries))),
                }
            }
        )
    return dic


def calculating_sj_salaries(vacancies):
    salaries = []
    for vacancy in vacancies:
        salary_from = vacancy['payment_from']
        salary_to = vacancy['payment_to']
        salaries.append(predict_salary(salary_from, salary_to))
    return salaries


def getting_sj_salaries(url, headers, payload):
    stop = True
    page_number = 0
    salaries = []
    while stop != False:
        payload['page'] = page_number
        response = requests.get(url, headers=headers, params=payload)
        response.raise_for_status()
        vacancies = response.json()
        salaries += calculating_sj_salaries(vacancies['objects'])
        stop = vacancies['more']
        vacancies_number = vacancies['total']
        page_number += 1
    return salaries, vacancies_number


def predict_rub_salary_sj(url, headers, payload, list):
    dic = {}
    for name in list:
        payload['keyword'] = name
        salaries, vacancies_number = getting_sj_salaries(url, headers, payload)
        sorted_salaries = [float(var) for var in salaries if var != None]
        dic.update(
            {name: {
                'vacabcies_found': str(vacancies_number),
                'vacancies_processed': str(len(sorted_salaries)),
                'average_salary': str(int(np.mean(sorted_salaries))),
            }
            }
        )
    return dic


def creature_table(dicts, table_title):
    table_data = [
        [
            'Язык программирования',
            'Вакансий найдено',
            'Вакансий обработано',
            'Средняя зарплата'
        ]
    ]
    for key, value in dicts.items():
        table_data.append(key.split() + list(value.values()))
    table = AsciiTable(table_data)
    table.title = table_title
    print(table.table)


if __name__ == '__main__':
    load_dotenv()

    secret_key = os.getenv('SECRET_KEY')

    specialization_list = [
        'Python',
        'JavaScrip',
        'Java',
        'Ruby',
        'PHP',
        'C++',
        'CSS',
        'C#',
    ]

    hh_url = 'https://api.hh.ru/vacancies'
    hh_payload = {
        'specialization': 1.221,
        'area': 1,
        'text': [],
        'page': [],
    }

    sj_url = 'https://api.superjob.ru/2.0/vacancies'
    sj_headers = {
        'X-Api-App-Id': secret_key
    }
    sj_payload = {
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

    hh_table_title = 'HeadHunter Moscow'
    sj_table_title = 'SuperJob Moscow'

    hh_programmer_salaries = predict_rub_salary_hh(hh_url, hh_payload,
                                                   specialization_list)
    sj_programmer_salaries = predict_rub_salary_sj(sj_url, sj_headers,
                                                   sj_payload,
                                                   specialization_list)

    creature_table(hh_programmer_salaries, hh_table_title)
    creature_table(sj_programmer_salaries, sj_table_title)
