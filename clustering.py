from __future__ import print_function
import numpy as np
import pandas as pd
import nltk
import re
import os
import codecs
from sklearn import feature_extraction
# import mpld3
from typing import List
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from metacritic_extraction import Movie
import pickle

stemmer = SnowballStemmer("english")
nltk.download('punkt')


# here I define a tokenizer and stemmer which returns the set of stems in the text that it is passed
def cluster_us(movie_list=None):
    # if not movie_list:

    summary_list = []
    films = []
    ranks = []
    genres = []

    for movie in movie_list:
        summary_list.append(movie.summary)
        films.append(movie.name)
        ranks.append(movie.metascore)
        genres.append(str(movie.genre))
    """this method gets a list of dictionaries and cluster the movies by it. """
    totalvocab_stemmed = []
    for i in range(len(summary_list)):
        allwords_stemmed = tokenize_and_stem(summary_list[i])  # for each item in 'synopses', tokenize/stem
        totalvocab_stemmed.extend(allwords_stemmed)  # extend the 'totalvocab_stemmed' list

    # define vectorizer parameters
    tfidf_vectorizer = TfidfVectorizer(max_df=0.8, max_features=200000,
                                       min_df=0.2, stop_words='english',
                                       use_idf=True, tokenizer=tokenize_and_stem, ngram_range=(1, 3))

    tfidf_matrix = tfidf_vectorizer.fit_transform(summary_list)  # fit the vectorizer to synopses

    print(tfidf_matrix.shape)
    terms = tfidf_vectorizer.get_feature_names()

    dist = 1 - cosine_similarity(tfidf_matrix)

    num_clusters = 5

    km = KMeans(n_clusters=num_clusters)

    km.fit(tfidf_matrix)

    clusters = km.labels_.tolist()

    # uncomment the below to save your model
    # since I've already run my model I am loading from the pickle

    joblib.dump(km, 'doc_cluster.pkl')

    km = joblib.load('doc_cluster.pkl')
    clusters = km.labels_.tolist()
    vocab_frame = pd.DataFrame({'words': totalvocab_stemmed}, index=totalvocab_stemmed)

    films = {'title': films, 'rank': ranks, 'synopsis': summary_list, 'cluster': clusters, 'genre': genres}

    frame = pd.DataFrame(films, index=clusters, columns=['title', 'rank', 'cluster', 'genre'])
    # frame = pd.DataFrame([films], index=[clusters], columns=['rank', 'title', 'cluster', 'genre'])

    print("Top terms per cluster:")
    print()
    # sort cluster centers by proximity to centroid
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]

    for i in range(num_clusters):
        print("Cluster %d words:" % i, end='')

        for ind in order_centroids[i, :6]:  # replace 6 with n words per cluster
            oahd = vocab_frame.loc[terms[ind].split(' ')]
            print(' %s' % vocab_frame.loc[terms[ind].split(' ')].values.tolist()[0][0].encode('utf-8', 'ignore'),
                  end=',')
        print()  # add whitespace;
        print()  # add whitespace

        print("Cluster %d titles:" % i, end='')
        for title in frame.loc[i]['title'].values.tolist():
            print(' %s,' % title, end='')
        print()  # add whitespace
        print()  # add whitespace

    print()
    print()


def tokenize_and_stem(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    stems = [stemmer.stem(t) for t in filtered_tokens]
    return stems


def tokenize_only(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    return filtered_tokens

# not super pythonic, no, not at all.
# use extend so it's a big flat list of vocab


# def tems_in_cluster(num_clusters,km):
#     print("Top terms per cluster:")
#     print()
#     # sort cluster centers by proximity to centroid
#     order_centroids = km.cluster_centers_.argsort()[:, ::-1]
#
#     for i in range(num_clusters):
#         print("Cluster %d words:" % i, end='')
#
#         for ind in order_centroids[i, :6]:  # replace 6 with n words per cluster
#             print(' %s' % vocab_frame.ix[terms[ind].split(' ')].values.tolist()[0][0].encode('utf-8', 'ignore'),
#                   end=',')
#         print()  # add whitespace
#         print()  # add whitespace
#
#         print("Cluster %d titles:" % i, end='')
#         for title in frame.ix[i]['title'].values.tolist():
#             print(' %s,' % title, end='')
#         print()  # add whitespace
#         print()  # add whitespace
#
#     print()
#     print()
