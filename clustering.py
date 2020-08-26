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
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from metacritic_extraction import Movie
import pickle
import plotly.express as px
import chart_studio
import os  # for os.path.basename

from sklearn.manifold import MDS

chart_studio.tools.set_credentials_file(username='Ahraking', api_key='n3uisowWWZcSGEgk3iyN')

stemmer2 = WordNetLemmatizer()
nltk.download("wordnet")
stemmer = SnowballStemmer("english")
nltk.download('punkt')


# here I define a tokenizer and stemmer which returns the set of stems in the text that it is passed
def cluster_us(movie_list=None):
    # if not movie_list:

    summary_list = []
    films = []
    ranks = []
    genres = []
    years = []
    foreigns = []
    languages = []
    countries = []

    for movie in movie_list:
        summary_list.append(movie.summary)
        films.append(movie.name)
        ranks.append(movie.metascore)
        genres.append(str(movie.genre))
        years.append(int(movie.year))
        foreigns.append(1 if movie.competition_category == 'FOREIGN LANGUAGE FILM' else 0)
        languages.append(movie.languages)
        countries.append(movie.countries)
    """this method gets a list of dictionaries and cluster the movies by it. """
    totalvocab_stemmed = []
    totalvocab_tokenized = []
    for i in range(len(summary_list)):
        allwords_stemmed = tokenize_and_stem(summary_list[i])  # for each item in 'synopses', tokenize/stem
        totalvocab_stemmed.extend(allwords_stemmed)  # extend the 'totalvocab_stemmed' list

        # allwords_tokenized = tokenize_only(summary_list[i])
        # totalvocab_tokenized.extend(allwords_tokenized)  # extend the 'totalvocab_stemmed' list

    # define vectorizer parameters
    tfidf_vectorizer = TfidfVectorizer(max_df=0.8, max_features=200000,
                                       min_df=0.2, stop_words='english',
                                       use_idf=True, tokenizer=tokenize_and_stem, ngram_range=(1, 1))
    # tfidf_vectorizered = TfidfVectorizer(max_df=0.8, max_features=200000,
    #                                    min_df=0.05, stop_words='english',
    #                                    use_idf=True, tokenizer=tokenize_only, ngram_range=(1, 3), max_df=0.8)
    tfidf_vectorizer = TfidfVectorizer(stop_words='english', lowercase=True, tokenizer=tokenize_and_stem,
                                       ngram_range=(1, 1), max_df=0.8, min_df=0.01)

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

    # joblib.dump(km, 'doc_cluster.pkl')
    #
    # km = joblib.load('doc_cluster.pkl')
    clusters = km.labels_.tolist()
    vocab_frame = pd.DataFrame({'words': totalvocab_stemmed}, index=totalvocab_stemmed)

    films = {'title': films, 'rank': ranks, 'synopsis': summary_list, 'cluster': clusters, 'genre': genres,
             'year': years, 'foreign': foreigns, 'language': languages, 'country': countries}

    frame = pd.DataFrame(films, index=clusters,
                         columns=['title', 'rank', 'cluster', 'genre', 'year', 'foreign', 'language', 'country'])
    print(frame['cluster'].value_counts())
    grouped = frame['rank'].groupby(frame['cluster'])  # groupby cluster for aggregation purposes

    print(grouped.mean())  # average rank (1 to 100) per cluster
    # frame = pd.DataFrame([films], index=[clusters], columns=['rank', 'title', 'cluster', 'genre'])

    print("Top terms per cluster:")
    frame.to_csv("finished_output.csv")
    # fig = px.scatter(frame, x='cluster', y='rank', color='cluster', hover_name='title', custom_data=['foreign'],
    #                  symbol='foreign')
    # chart_studio.plotly.plot(fig, filename='interactive_clustering', auto_open=True)
    # fig.show()
    print()
    # sort cluster centers by proximity to centroid
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    with open("nimni", "w") as f:
        for i in range(num_clusters):
            f.write("Cluster %d words:" % i)
            print("Cluster %d words:" % i, end='')

            for ind in order_centroids[i, :5]:  # replace 6 with n words per cluster
                print(terms[ind])
                f.write(' %s' % vocab_frame.loc[terms[ind].split(' ')].values.tolist()[0][0].encode('utf-8', 'ignore'))
                # print(' %s' % vocab_frame.loc[terms[ind].split(' ')].values.tolist()[0][0].encode('utf-8', 'ignore'),
                #       end=',')
            print()  # add whitespace;
            print()  # add whitespace

            print("Cluster %d titles:" % i, end='')
            f.write("Cluster %d titles:" % i)
            titles = frame.loc[i]['title']
            f.write(str(titles))

            print(titles)
            print()  # add whitespace
            print()  # add whitespace

        print()
        print()
        MDS()

        # convert two components as we're plotting points in a two-dimensional plane
        # "precomputed" because we provide a distance matrix
        # we will also specify `random_state` so the plot is reproducible.
        mds = MDS(n_components=2, dissimilarity="precomputed", random_state=1)

        pos = mds.fit_transform(dist)  # shape (n_components, n_samples)

        xs, ys = pos[:, 0], pos[:, 1]
        frame = pd.DataFrame(dict(x=xs, y=ys, title=frame['title'], foreign=foreigns, cluster=clusters))
        # groups = frame.groupby('label')
        fig = px.scatter(frame, x='x', y='y', color='cluster', symbol='foreign',hover_name='title')
        chart_studio.plotly.plot(fig, filename='interactive_clustering_mds', auto_open=True)


def tokenize_and_stem(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    filtered_tokens_set = set()
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    stop_words = stopwords.words('english')
    stop_words.append("\'s")
    for token in tokens:
        if re.search('[a-zA-Z]', token) and token not in stop_words:
            filtered_tokens.append(token)
            filtered_tokens_set.add(token)
    stems = [stemmer.stem(t) for t in filtered_tokens]
    # stems = [stemmer2.lemmatize(t) for t in filtered_tokens]

    # stems = [stemmer.stem(t) for t in filtered_tokens_set]
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
