from metacritic_extraction import CSVParser
from clustering import cluster_us

hey = "hi"
ohad = CSVParser("awards_by_films_shortened.csv")
ohad.write_to_file()
too = cluster_us(ohad.movies)
roy = "aaaa"
