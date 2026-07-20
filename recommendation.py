import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

movies = pd.read_csv("tmdb_5000_movies.csv")

movies = movies[['title','genres']]

cv = CountVectorizer(max_features=5000, stop_words='english')

vectors = cv.fit_transform(movies['genres'].astype(str)).toarray()

similarity = cosine_similarity(vectors)

pickle.dump(similarity, open("similarity.pkl","wb"))

movies.to_csv("movies.csv", index=False)