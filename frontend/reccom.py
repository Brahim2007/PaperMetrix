from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel,cosine_similarity
import pickle
import pandas as pd
import numpy as np



def get_similar_items(query,start=0,end=50,get_scores=False):
    dict__ = {"id":[],"abstract":[],"title":[],"keywords":[],"joined":[]}
    from api.models import Article

    for i in Article.objects.all():
        dict__['id'].append(i.pk)
        dict__['title'].append(i.title)
        dict__['abstract'].append(i.abstract)
        kw = '' if i.keywords is None else " ".join(list(i.keywords))
        dict__['keywords'].append(kw)

        dict__['joined'].append(f"{i.title} {i.abstract} {i.source} {i.type}")

    tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0, stop_words='english')
    tf_fit = tf.fit(dict__['joined'])
    tfidf_matrix = tf.fit_transform(dict__['joined'])


    # tfidf_matrix = pickle.load(open("tfidf.pickle","rb"))
    # tf_fit = pickle.load(open("tfidf_fit.pickle","rb"))
    results = {}
    que = tf_fit.transform([query])
    sim_ = cosine_similarity(tfidf_matrix,que).reshape(1,-1)[0]
    similar_indices = sim_.argsort()[::-1][start:end]
    if get_scores:
        similar_items = [(dict__['id'][i],sim_[i]) for i in similar_indices]
        return np.array(similar_items)
    else:
        similar_items = [dict__['id'][i] for i in similar_indices]

    return similar_items
