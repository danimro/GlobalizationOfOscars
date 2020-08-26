from metacritic_extraction import CSVParser, Movie
from pickle import loads, load

# ohad = CSVParser().start("awards_by_films_shortened.csv")
# with open("pickled.roy", "wb") as f:
#     f.write(pickle.dumps(ohad.movies))

with open("pickled.roy", "rb") as f:
    ohad = load(f)
    nim = "nam"