import requests
import math
from terminaltables import AsciiTable
import os
from dotenv import load_dotenv


def predict_salary(salary_from, salary_to):
    if salary_from:
        if salary_to:
            average_salary = (salary_from + salary_to) / 2
        else:
            average_salary = salary_from * 1.2
    else:
        if salary_to:
            average_salary = salary_to * 0.8
        else:
            average_salary = None
    return average_salary


def predict_rub_salary_hh(job_title):
    vacancies = []
    url = 'https://api.hh.ru/vacancies'
    payload = {'text': job_title,
               'area': 1,
               'period': 30}
    response = requests.get(url, params=payload)
    response.raise_for_status()
    response_data = response.json()


    for page in range(response_data['pages'] + 1):
        payload = {'text': job_title,
                   'area': 1,
                   'period': 30,
                   'page': page}
        response = requests.get(url, params=payload)
        response.raise_for_status()
        response_data = response.json()

        vacancies.extend(response_data['items'])

    vacancies_found = response_data['found']
    average_salaries = []
    vacancies_processed = 0
    salaries_sum = 0

    for vacancy in vacancies:
        if vacancy['salary']:
            if vacancy['salary']['currency'] == 'RUR':
                average_salary = predict_salary(vacancy['salary']['from'],
                                                vacancy['salary']['to'])
                average_salaries.append(average_salary)
            else:
                average_salary = None
                average_salaries.append(average_salary)
        else:
            average_salary = None
            average_salaries.append(average_salary)

    for salary in average_salaries:
        if salary:
            vacancies_processed += 1
            salaries_sum += salary

    average_salary = int(salaries_sum / vacancies_processed)

    return vacancies_found, vacancies_processed, average_salary


def predict_rub_salary_sj(job_title):
    url = 'https://api.superjob.ru/2.0/vacancies'
    headers = {'X-Api-App-Id': SJOB_TOKEN}
    payrole = {
        'catalogues': 48,
        'town': 4,
        'period': 30,
        'keywords': job_title
    }
    response = requests.get(url, headers=headers, params=payrole)
    response.raise_for_status()
    response_data = response.json()

    vacancies = []
    vacancies_found = response_data['total']
    page_amount = math.ceil(vacancies_found / 20)

    for page in range(page_amount + 1):
        payrole = {
            'catalogues': 48,
            'town': 4,
            'period': 30,
            'keywords': job_title,
            'page': page
        }
        response = requests.get(url, headers=headers, params=payrole)
        response.raise_for_status()
        response_data = response.json()
        vacancies.extend(response_data['objects'])

    average_salaries = []
    vacancies_processed = 0
    salaries_sum = 0

    for vacancy in vacancies:
        if vacancy['currency'] == 'rub':
            average_salary = predict_salary(vacancy['payment_from'],
                                            vacancy['payment_to'])
            average_salaries.append(average_salary)
        else:
            average_salary = None
            average_salaries.append(average_salary)


    for salary in average_salaries:
        if salary:
            vacancies_processed += 1
            salaries_sum += salary

    average_salary = int(salaries_sum / vacancies_processed)

    return vacancies_found, vacancies_processed, average_salary


def fill_salary_data(func):
    salary_data = {}
    for language in languages:
        job_title = 'Программист ' + language
        vacancy_data = func(job_title)
        salary_for_language = {'vacancies_found': vacancy_data[0],
                               'vacancies_processed': vacancy_data[1],
                               'average_salary': vacancy_data[2]
                               }
        salary_data[language] = salary_for_language
    return salary_data


def draw_ascii_table(salary_for_language_data, title):
    salary_table_data = [('Язык программирования', 'Вакансий найдено',
                          'Вакансий обработано', 'Средняя зарплата')]
    for language in salary_for_language_data:
        data_for_table = (language, salary_for_language_data[language]['vacancies_found'],
                          salary_for_language_data[language]['vacancies_processed'],
                          salary_for_language_data[language]['average_salary'])
        salary_table_data.append(data_for_table)

    table_instance = AsciiTable(salary_table_data, title)
    table_instance.justify_columns[2] = 'right'
    print(table_instance.table)
    print()


if __name__ == '__main__':
    load_dotenv()
    SJOB_TOKEN = os.getenv('SJOB_TOKEN')

    languages = ['Python', 'JavaScript', 'Java', 'C++',
                 'Ruby', 'PHP', 'C#', 'C', 'TypeScript', 'Go']

    salary_for_languages_sj = fill_salary_data(predict_rub_salary_sj)
    salary_for_languages_hh = fill_salary_data(predict_rub_salary_hh)

    draw_ascii_table(salary_for_languages_hh, 'HeadHunter, Moscow')
    draw_ascii_table(salary_for_languages_sj, 'SuperJob, Moscow')
