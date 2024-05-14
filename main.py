import json
import requests
from fake_headers import Headers
from bs4 import BeautifulSoup

keywords = ['Django', 'Flask']

url = 'https://spb.hh.ru/search/vacancy?'
params = {
    'area': [1, 2],
    'text': 'python',
    'page': 0
}


def get_headers():
    headers_generator = Headers(os='win', browser='firefox')
    return headers_generator.generate()


def hh_parse(keys, urls, parametrs):
    response = requests.get(url=urls, params=parametrs, headers=get_headers())
    response.encoding = 'utf-8'
    main_html_data = response.text
    main_soup = BeautifulSoup(main_html_data, 'lxml')

    vacancy_list = main_soup.find('div', id='a11y-main-content')
    vacancies = vacancy_list.find_all('div', class_='serp-item serp-item_simple serp-item_link serp-item-redesign')

    vacancy_data = []
    for vacancy in vacancies:
        vacancy_link = vacancy.find('a').get('href')
        vacancy_title = vacancy.find('h2').text.strip()

        company = vacancy.find('span', class_='company-info-text--O32pGCRW0YDmp3BHuNOP').text
        # company = "".join([char for char in company if (char >= 'a' and char <= 'z') or (char >= 'A' and char <=
        # 'Z') or ( char >= "А" and char <= 'Я') or (char >= 'а' and char <= 'я') or char in '0123456789₽$' or char
        # == ' '])
        city = vacancy.select("span[class='fake-magritte-primary-text--qmdoVdtVX3UWtBb3Q7Qj']")[0].text

        salary = "Не указана"
        salary_in_html = vacancy.find('span', class_='compensation-text--cCPBXayRjn5GuLFWhGTJ '
                                                     'fake-magritte-primary-text--qmdoVdtVX3UWtBb3Q7Qj '
                                                     'separate-line-on-xs--pwAEUI79GJbGDu97czVC')
        if salary_in_html:
            salary = salary_in_html.text

            # salary = "".join([char for char in salary if (char >= 'a' and char <= 'z') or (char >= 'A' and char <=
            # 'Z') or ( char >= "А" and char <= 'Я') or ( char >= 'а' and char <= 'я') or char in '0123456789₽$' or
            # char == ' '])

        # if "$" not in salary:
        #         continue

        response = requests.get(vacancy_link, headers=get_headers())
        offer_html_data = response.text
        offer_soup = BeautifulSoup(offer_html_data, features='lxml')

        offer_body_tag = offer_soup.find('div', class_='g-user-content')
        if offer_soup.find('div', class_='g-user-content') is not None:
            offer_text = offer_body_tag.text.strip()
        else:
            offer_text = 'Не указано'

        key_pass = []
        offer_text = offer_text.lower()
        for kw in keys:
            if kw.lower() in offer_text:
                key_pass.append(True)
            else:
                key_pass.append(False)
        if not all(key_pass):
            continue

        # if len(dollar_check_set) == 0 or dollar_check_set[0] not in salary.strip():
        #     continue

        vacancy_data.append(
            {
                "Вакансия": vacancy_title,
                "Ссылка": vacancy_link,
                "Зарплата": salary,
                "Название компании": company,
                "Город": city
            }
        )

    print(f'Найдено {len(vacancy_data)} подходящих вакансий')
    for item in vacancy_data:
        print(item)
    return vacancy_data


def save_to_file(data):
    with open('vacancys.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=5)


if __name__ == '__main__':
    parse_data = hh_parse(keywords, url, params)
    save_to_file(parse_data)
