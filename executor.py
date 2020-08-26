from metacritic_extraction import CSVParser, Movie
from pickle import load
from clustering import cluster_us
with open("pickled.roy", "rb") as f:
    parser = load(f)
cluster_us(parser)
roy = "aaaa"
