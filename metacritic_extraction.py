# To get the url, and scrap the html page
import requests
from bs4 import BeautifulSoup, element
# To save the reviews in a dataframe
import pandas as pd

url = "https://www.metacritic.com/movie/get-out/details"

movies = []

att = ['year', 'name', 'metascore', 'summary', 'genre']


def extract_summary(soup: BeautifulSoup):
    return str(soup.find_all('div', class_="summary")[0].contents[3].contents[0])


def extract_name_and_year(soup: BeautifulSoup):
    name = str(soup.find_all('div', class_='product_page_title oswald upper')[0].contents[1].contents[0].contents[0])
    date = soup.find_all('span', class_='release_date')[0].contents[3].contents[0]
    year = int(date[date.find(',') + 1:])
    return {'name': name, 'year': year}


def extract_metascore(soup: BeautifulSoup):
    return int(soup.find_all('span', class_='metascore_w larger movie positive')[0].contents[0])


def extract_genre(soup: BeautifulSoup):
    genres_array_tag = soup.find_all('tr', class_='genres')[0].contents[3]
    genres_array = [i.contents[0] for i in genres_array_tag if isinstance(i, element.Tag)]
    return genres_array


def extract_language(soup: BeautifulSoup):
    """return array of languages"""
    languages_array_tag = soup.find_all('tr', class_='languages')[0].contents[3]
    languages_array = [i.contents[0] for i in languages_array_tag if isinstance(i, element.Tag)]
    return languages_array
    # return str(soup.find_all('tr', class_='languages')[0].contents[3].contents[1].contents[0])


def extract_country(soup: BeautifulSoup):
    country_array_tag = soup.find_all('tr', class_='countries')[0].contents[3]
    country_array = [i.contents[0] for i in country_array_tag if isinstance(i, element.Tag)]
    return country_array


def extract_params(url: str) -> dict:
    user_agent = {'User-agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=user_agent)
    soup = BeautifulSoup(response.text, 'html.parser')
    review_dict = {}
    review_dict = extract_name_and_year(soup)
    review_dict['summary'] = str(extract_summary(soup))
    review_dict['metascore'] = extract_metascore(soup)
    review_dict['genre'] = extract_genre(soup)
    review_dict['languages'] = extract_language(soup)
    review_dict['countries'] = extract_country(soup)
    return review_dict


review_dict = extract_params(url)
