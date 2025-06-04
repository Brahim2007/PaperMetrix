from django.shortcuts import reverse,redirect
from .utils import *
from api.models import Article, Tag
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from mendeley import Mendeley
from mendeley.session import MendeleySession

def get_article_from_data(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            query = request.POST['query'].split(';')
            mendeley = Mendeley(settings.MENDELEY_ID, settings.MENDELEY_SECRET)
            auth = mendeley.start_client_credentials_flow().authenticate()


            for i in query:
                if query == '': continue
                get_data_by_query(auth.token['access_token'],query=i)

            if request.user.keywords:
                for i in request.user.keywords:
                    get_data_by_query(auth.token['access_token'],query=i)

            if request.user.authors:
                for i in request.user.authors:
                    get_article_from_authors(i,auth.token['access_token'])

            if request.user.tags:
                for i in request.user.tags:
                    get_data_by_query(auth.token['access_token'],query=i)

            return JsonResponse({"success":"Success"})

@login_required
def add_tag(request,pk):
    tag = request.POST.get('tag')
    arti = Article.objects.get(pk=pk)
    if tag:
        tag,_ = Tag.objects.get_or_create(tag=tag,user=request.user)
        tag.article.add(arti)
        return JsonResponse({'tag':tag.tag,'pk':tag.pk},status=200)
    return JsonResponse({},status=500)

@login_required
def remove_tag(request,pk):
    try:
        tag = Tag.objects.get(pk=pk)
        if request.user == tag.user:
            tag.delete()
    except Tag.DoesNotExist:
        pass
    return JsonResponse({"success":"Success"})

def get_tweets(request, pk):
    """Return tweets for a given article."""
    try:
        obj = Article.objects.get(pk=pk)
        if obj.twitter_data.get("tweets") is None:
            tweets = twitter_from_doi(obj.title, obj.identifiers.get("doi"))
            obj.twitter_data = {"tweets": tweets}
            obj.save()
            return JsonResponse({"tweets": tweets})
        return JsonResponse({"tweets": obj.twitter_data.get("tweets")})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
