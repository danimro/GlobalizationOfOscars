# To get the url, and scrap the html page
import requests
from bs4 import BeautifulSoup, element
# To save the reviews in a dataframe
import pandas as pd
import re
import csv

regex = re.compile(r"https:\/\/www\.metacritic\.com\/movie\/.+\/details")
regex_for_name_extraction = re.compile(r"https:\/\/www\.metacritic\.com\/movie\/(.+)")


def wrapper(some_function):
    def inner(*args, **kwargs):
        try:
            return some_function(*args, **kwargs)
        except Exception as e:
            return None

    return inner


class CSVParser:
    def __init__(self, filename: str):
        self.movies = set()
        with open(filename, "r") as csv_file:
            line_count = 0
            lines_iterator = csv.reader(csv_file)
            for line in lines_iterator:
                if line_count != 0:
                    movie = Movie(*line)
                    print(movie)
                    if movie.url:
                        self.movies.add(movie)
                line_count += 1

    def write_to_file(self):
        with open("output.csv", "w") as csv_to_write:
            writer = csv.writer(csv_to_write, delimiter=',')
            column_names = ["name", "year", "competition_category", "winner", "url", "summary",
                            "countries", "languages", "genre", "metascore"]
            writer.writerow(column_names)
            for movie in self.movies:
                writer.writerow(movie.to_line())


class Movie:
    @staticmethod
    def find_url(movie_name: str) -> str or None:
        query = f'{movie_name} metacritic details'
        for j in search(query, tld="com", num=8, stop=10, pause=0.8):
            match = regex.match(j)
            if match:
                url = match.group(0)
                return url
            else:
                match = regex_for_name_extraction.match(j)
                if match:
                    name = match.group(1)
                    url = f'https://www.metacritic.com/movie/{name}/details'
                    return url
        return None

    def __eq__(self, other):
        return self.entity == other.entity

    def __hash__(self):
        return hash(self.entity)

    def __init__(self, year: str, competition_category: str, winner: str, entity: str):
        """
        Constructor. Gets parameter from CSV , looks for google the specific metacritic URL and parses the details
        page with BeautifulSoup.
        :param competition_category:
        :param winner:
        :param entity:
        """
        self.url = Movie.find_url(entity)
        self.entity = entity
        self.competition_category = competition_category
        self.winner = True if winner == 'TRUE' else False
        if self.url:
            user_agent = {'User-agent': 'Mozilla/5.0'}
            response = requests.get(self.url, headers=user_agent)
            soup = BeautifulSoup(response.text, 'html.parser')
            self.summary = Movie.extract_summary(soup)
            self.name = Movie.extract_name(soup)
            self.year = int(year)
            self.summary = str(Movie.extract_summary(soup))
            self.metascore = Movie.extract_metascore(soup)
            self.genre = Movie.extract_genre(soup)
            self.languages = Movie.extract_language(soup)
            self.countries = Movie.extract_country(soup)
        self.winner = winner
        self.competition_category = competition_category

    @staticmethod
    @wrapper
    def extract_summary(soup: BeautifulSoup):
        return str(soup.find_all('div', class_="summary")[0].contents[3].contents[0])

    @staticmethod
    @wrapper
    def extract_name(soup: BeautifulSoup):
        name = str(
            soup.find_all('div', class_='product_page_title oswald upper')[0].contents[1].contents[0].contents[0])
        # date = soup.find_all('span', class_='release_date')[0].contents[3].contents[0]
        # year = int(date[date.find(',') + 1:])
        return name

    @staticmethod
    @wrapper
    def extract_metascore(soup: BeautifulSoup):
        tag = soup.find_all('span', class_='metascore_w larger movie positive') or soup.find_all('span',
                                                                                                 class_='metascore_w larger movie mixed')
        return int(tag[0].contents[0])

    @staticmethod
    @wrapper
    def extract_language(soup: BeautifulSoup):
        """return array of languages"""
        languages_array_tag = soup.find_all('tr', class_='languages')[0].contents[3]
        languages_array = [i.contents[0] for i in languages_array_tag if isinstance(i, element.Tag)]
        return languages_array
        # return str(soup.find_all('tr', class_='languages')[0].contents[3].contents[1].contents[0])

    @staticmethod
    @wrapper
    def extract_genre(soup: BeautifulSoup):
        genres_array_tag = soup.find_all('tr', class_='genres')[0].contents[3]
        genres_array = [i.contents[0] for i in genres_array_tag if isinstance(i, element.Tag)]
        return genres_array

    @staticmethod
    @wrapper
    def extract_country(soup: BeautifulSoup):
        country_array_tag = soup.find_all('tr', class_='countries')[0].contents[3]
        country_array = [i.contents[0] for i in country_array_tag if isinstance(i, element.Tag)]
        return country_array

    def to_line(self):
        return [self.name, self.year, self.competition_category, self.winner, self.url, self.summary,
                str(self.countries), str(self.languages), str(self.genre), str(self.metascore)]

    def __repr__(self):
        return f'Movie:{self.entity}, url: {self.url}'


url = "https://www.metacritic.com/movie/get-out/details"

try:
    from googlesearch import search
except ImportError:
    print("No module named 'google' found")


@wrapper
def divide_by_number(x, y):
    return x / y


line_to_test = "1998,FOREIGN LANGUAGE FILM,FALSE,The Grandfather".split(",")
ohad = Movie(*line_to_test)

t = "asd"
ohad = CSVParser("awards_by_films.csv")
too = "boo"
ohad.write_to_file()
