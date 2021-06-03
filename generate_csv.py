import pandas as pd
import requests
from api.models import Article
from django.db.models import ObjectDoesNotExist

dict__ = {"id":[],"abstract":[],"title":[],"keywords":[],"joined":[]}

for i in Article.objects.all():
    dict__['id'].append(i.pk)
    dict__['title'].append(i.title)
    dict__['abstract'].append(i.abstract)
    kw = '' if i.keywords is None else " ".join(list(i.keywords))
    dict__['keywords'].append(kw)

    dict__['joined'].append(f"{i.title} {i.abstract} {i.source} {i.type}")


csv = pd.DataFrame(dict__)
csv.to_csv('csv.csv')
