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
    vacancies_search_response = response.json()


    for page in range(vacancies_search_response['pages'] + 1):
        payload = {'text': job_title,
                   'area': 1,
                   'period': 30,
                   'page': page}
        response = requests.get(url, params=payload)
        response.raise_for_status()
        vacancies_search_response = response.json()

        vacancies.extend(vacancies_search_response['items'])

    vacancies_found = vacancies_search_response['found']
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
    headers = {'X-Api-App-Id': sjob_token}
    payrole = {
        'catalogues': 48,
        'town': 4,
        'period': 30,
        'keywords': job_title
    }
    response = requests.get(url, headers=headers, params=payrole)
    response.raise_for_status()
    vacancies_search_response = response.json()

    vacancies = []
    vacancies_found = vacancies_search_response['total']
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
        vacancies_search_response = response.json()
        vacancies.extend(vacancies_search_response['objects'])

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


def fill_salary_specs(func):
    salary_for_languages = {}
    for language in languages:
        job_title = 'Программист ' + language
        vacancy_specs = func(job_title)
        salary_for_language = {'vacancies_found': vacancy_specs[0],
                               'vacancies_processed': vacancy_specs[1],
                               'average_salary': vacancy_specs[2]
                               }
        salary_for_languages[language] = salary_for_language
    return salary_for_languages


def draw_ascii_table(salary_for_language, title):
    salary_table = [('Язык программирования', 'Вакансий найдено',
                          'Вакансий обработано', 'Средняя зарплата')]
    for language in salary_for_language:
        specs_for_table = (language, salary_for_language[language]['vacancies_found'],
                          salary_for_language[language]['vacancies_processed'],
                          salary_for_language[language]['average_salary'])
        salary_table.append(specs_for_table)

    table_instance = AsciiTable(salary_table, title)
    table_instance.justify_columns[2] = 'right'
    print(table_instance.table)
    print()


if __name__ == '__main__':
    load_dotenv()
    sjob_token = os.getenv('SJOB_TOKEN')

    languages = ['Python', 'JavaScript', 'Java', 'C++',
                 'Ruby', 'PHP', 'C#', 'C', 'TypeScript', 'Go']

    salary_for_languages_sj = fill_salary_specs(predict_rub_salary_sj)
    salary_for_languages_hh = fill_salary_specs(predict_rub_salary_hh)

    draw_ascii_table(salary_for_languages_hh, 'HeadHunter, Moscow')
    draw_ascii_table(salary_for_languages_sj, 'SuperJob, Moscow')
