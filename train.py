
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel,cosine_similarity
import pickle
import pandas as pd
csv = pd.read_csv('csv.csv')

tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0, stop_words='english')
tf_fit = tf.fit(csv['joined'])
tfidf_matrix = tf.fit_transform(csv['joined'])
pickle.dump(tfidf_matrix,open("tfidf.pickle","wb"))
pickle.dump(tf_fit,open("tfidf_fit.pickle","wb"))
