import django
from django.shortcuts import render
from django.http import JsonResponse,HttpResponseRedirect
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.
from django.shortcuts import render,redirect,reverse
from django.urls import translate_url
from mendeley.session import MendeleySession
from django.views.generic import ListView,DetailView,TemplateView
from django.db.models import Sum,Count,Max
from django.utils import translation

from api.models import *
import json
import collections
from mendeley import Mendeley

from .utils import get_article_from_authors, get_data, get_data_by_query
from api.deepseek_client import recommend_articles
from .reccom import *
from .services.recommendation_service import (
    summarize_reader_data,
    library_recommendations,
    recommend_with_fallback,
)
import random
import requests
import re

def home(request):
    if request.session.get('lan') is None:
        request.session['lan'] = 'English'
    return render(request,'frontend/index.html')

class GetAuthor(DetailView):
    model = Authors
    template_name = 'frontend/author.html'
    def get(self,request,*args,**kwargs):
        super(GetAuthor,self).get(request,*args,**kwargs)
        self.object = self.get_object()
        context = super().get_context_data()

        paginator = Paginator(context['object'].article_set.all().order_by('-count'), 25)
        page_number = request.GET.get('page',1)
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj

        return render(request,self.template_name,context)

class LibaraySet(ListView):
    model = Library
    template_name = 'frontend/library_list.html'
    def get(self,request,**kwargs):
        super().get(request,**kwargs)
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        self.object_list = self.get_queryset().all().filter(user=request.user)
        context = super().get_context_data()
        context['object_list'] = self.object_list

        return render(request,self.template_name,context)

    def post(self,request,**kwargs):

        library = Library(name=request.POST['name'],user=request.user)
        library.save()

        return HttpResponseRedirect(request.build_absolute_uri())

class LibraryDetail(DetailView):
    model = Library
    template_name = 'frontend/library_detail.html'
    def post(self,request,**kwargs):

        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))

        id = request.POST['id']
        self.get_object().articles.remove(Article.objects.get(pk=id))

        return HttpResponseRedirect(request.build_absolute_uri())

def delete_library(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    if request.method == 'POST':
        Library.objects.get(pk=request.POST['id']).delete()
    return HttpResponseRedirect(reverse('library'))

def search(request):
    if 'search' in request.GET:
        try:
            if request.GET['search'] in cache:
                article_list = Article.objects.all().filter(id__in=cache.get(request.GET['search']))
                return render(request,'frontend/search.html',{'article_list':article_list})
        except django.core.cache.backends.base.InvalidCacheBackendError:
            pass

        mendeley = Mendeley(settings.MENDELEY_ID, settings.MENDELEY_SECRET)
        auth = mendeley.start_client_credentials_flow().authenticate()
        request.session['token'] = auth.token
        ids = get_data_by_query(auth.token['access_token'],request.GET['search'],50)

        cache.set(request.GET['search'],ids,timeout=2000)

        article_list = Article.objects.all().filter(id__in=ids)

        return render(request,'frontend/search.html',{'article_list':article_list})
    return redirect(reverse('home'))

def add_to_library(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            id,lib_id = request.POST['id'],int(request.POST['lib_id'])
            library = request.user.library_set.get(pk=lib_id)
            art = Article.objects.get(pk=id)

            if art not in list(library.articles.all()): library.articles.add(art)
            return JsonResponse({"success":"success"})
    return JsonResponse({"error":"error"},status=404)

def load_articles_author(request):
    if request.user.is_authenticated:
        if request.method == 'POST':

            author = Authors.objects.get(pk=request.POST['pk'])
            mendeley = Mendeley(settings.MENDELEY_ID, settings.MENDELEY_SECRET)
            auth = mendeley.start_client_credentials_flow().authenticate()

            ids = get_article_from_authors(author.name,auth.token['access_token'])
            articles = Article.objects.filter(pk__in = ids)

            return JsonResponse({'id':list(articles.values_list("pk",flat=True)),'title':list(articles.values_list("title",flat=True))})


def get_article_data(request):
    if request.method == "POST":
        article_list = Article.objects.all().order_by('-count')

        paginator = Paginator(article_list, 25)
        page_number = request.POST['page_number']
        page_obj = paginator.get_page(page_number)
        return JsonResponse({"id":list(page_obj.object_list.values_list("id",flat=True)),"has_previous":page_obj.has_previous(),"has_next":page_obj.has_next(),"total":paginator.num_pages})


def get_readers(request,id):
    if request.method == "GET":
        article = Article.objects.get(pk=id)
        data = summarize_reader_data(article)
        return JsonResponse(data)


def topics(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    return render(request,"frontend/topics.html",{"disciplines":settings.SUBDISCIPLINES})

@login_required
@require_http_methods(["POST"])
def add_remove_topic(request):
    if request.method == "POST":
        tag = request.POST["tag"]
        
        if request.POST["add"]=='1':
            tags = [] if request.user.tags is None else list(request.user.tags)
            if tag not in tags:
                tags.append(tag)
                request.user.tags = tags
                request.user.save()
        else:
            tags = request.user.tags
            tags.remove(tag)
            request.user.tags = tags
            request.user.save()

        return JsonResponse({"success":"success"})

@login_required
@require_http_methods(["POST"])
def add_or_remove_kw(request):
    if request.method == "POST":
        keyword = json.loads(request.POST['data'])['keywords']
        user = request.user

        if request.POST["add"]=='1':
            keywords = [] if user.keywords is None else list(user.keywords)

            keywords.append(re.sub(' ','',keyword))
            user.keywords = keywords
            user.save()
        else:
            keywords = user.keywords
            keywords.remove(keyword)
            user.keywords = keywords
            user.save()
        return JsonResponse({"success":"success"})

@login_required
@require_http_methods(["POST"])
def add_or_remove_author(request):
    if request.method == "POST":
        author = json.loads(request.POST['data'])['authors']
        user = request.user

        if request.POST["add"]=='1':
            authors = [] if user.authors is None else list(user.authors)

            authors.append(author)
            user.authors = authors
            user.save()
        else:
            authors = user.authors
            authors.remove(author)
            user.authors = authors
            user.save()
        return JsonResponse({"success":"success"})

class DetailArticleAPI(DetailView):
    model = Article

    def get(self,request,pk):
        super(DetailArticleAPI,self).get(request,pk)
        article = Article.objects.get(pk=pk)
        return JsonResponse({"pk":pk,"title":article.title,"publisher":article.publisher,"year":article.year,"authors":list(article.authors.all().values_list("name",flat=True))})


class DetailArticle(DetailView):
    model = Article
    template_name = "frontend/detail.html"
    def get(self,request,pk):
        """Render detail view for an article with smart recommendations."""
        super().get(request,pk)
        self.object = self.get_object()
        context = self.get_context_data()
        from api.models import Vote
        try:
            rev = Vote.objects.get(user=request.user, article=self.object)
            context['upvoted'] = rev.vote_type == 'up'
            context['downvoted'] = rev.vote_type == 'down'
        except Vote.DoesNotExist:
            pass
        except TypeError:
            pass

        # Prefer recommendations from the DeepSeek API when available. If the
        # API returns nothing or fails we fall back to the TF‑IDF based
        # keyword recommender.
        context['ids'] = []
        prompt = f"{self.object.title} {self.object.abstract} {' '.join(self.object.keywords or [])}"
        rec_ids = recommend_with_fallback(prompt, limit=20)

        for _id in rec_ids:
            try:
                art = Article.objects.get(pk=_id)
            except Article.DoesNotExist:
                continue
            context['ids'].append({'title': art.title, 'id': art.pk})

        if self.object.identifiers.get('doi'):
            re = requests.get(f'https://api.altmetric.com/v1/doi/{self.object.identifiers.get("doi")}')

            if re.ok :
                context['altmetric'] = re.json()
                self.object.score = int(context['altmetric']['score'])
                self.object.save()
        return render(request,self.template_name,context)


    def post(self,request,*args,**kwargs):
        body = request.POST['comment']
        self.object = self.get_object()
        comment = Comment(user=request.user,article=self.object,body=body)
        comment.save()
        return HttpResponseRedirect(request.path_info)

def recomed(request):
    if request.user.is_authenticated:
        return render(request,'frontend/your_rec.html')
    return redirect(reverse('login'))

def update_review(request):
    if request.user.is_authenticated:
        rating = int(request.POST['rating'])
        pk = request.POST['pk']
        article = Article.objects.get(pk=pk)
        vote_type = 'up' if rating == 1 else 'down'
        from api.models import Vote
        vote, created = Vote.objects.get_or_create(article=article, user=request.user,
                                                  defaults={'vote_type': vote_type})
        if not created and vote.vote_type != vote_type:
            vote.vote_type = vote_type
            vote.save()

        return JsonResponse({"rate": article.upvotes - article.downvotes})

def get_recommendation(request):
    if request.user.is_authenticated:
        query = request.POST['query']
        reccom = get_similar_items(query,1,100)
        res = [{'title':i.title,'id':i.pk} for i in Article.objects.filter(pk__in = reccom)]
        return JsonResponse(res)
    return JsonResponse({'error':"error"})

def get_article(request):
    # if request.user.is_authenticated:
    article_list = Article.objects.all().order_by('-final_score')[:1000]
    res = [{'title':i.title,'id':i.pk,'vote':i.upvotes - i.downvotes,'rate':i.check_up_down(request.user)} for i in article_list]
    return JsonResponse(res,safe=False)

def get_article_top(request):
    # if request.user.is_authenticated:
    article_list = Article.objects.all().order_by('-comm_count')[:1000]
    res = [{'title':i.title,'id':i.pk,'vote':i.upvotes - i.downvotes,'rate':i.check_up_down(request.user)} for i in article_list]
    return JsonResponse(res,safe=False)

def get_article_new(request):
    # if request.user.is_authenticated:
    article_list = Article.objects.all().order_by('-add_on')[:1000]
    res = [{'title':i.title,'id':i.pk,'vote':i.upvotes - i.downvotes,'rate':i.check_up_down(request.user)} for i in article_list]
    return JsonResponse(res,safe=False)

def get_article_trending(request):
    article_list = Article.objects.all().order_by("-count")[:1000]
    res = [{"title":i.title,"id":i.pk,"vote":i.get_total(),"rate":i.check_up_down(request.user)} for i in article_list]
    return JsonResponse(res,safe=False)

def get_library_reccomendation(request,pk):
    if request.user.is_authenticated:
        lib = Library.objects.get(pk=pk)
        arts = library_recommendations(lib)
        return JsonResponse(arts, safe=False)


def smart_recommendations(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'auth required'}, status=403)

    from api.models import Vote

    abstracts = []
    for vote in Vote.objects.filter(user=request.user, vote_type='up'):
        abstracts.append(vote.article.abstract)

    keywords = request.user.keywords or []
    tags = request.user.tags or []
    prompt = ' '.join(keywords + tags + abstracts)
    rec_ids = recommend_articles(prompt)
    articles = Article.objects.filter(pk__in=rec_ids)
    data = [{'title': a.title, 'id': a.pk} for a in articles]
    return JsonResponse({'recommendations': data})


def change_lan(request,lan):
    translation.activate(lan)
    request.session['lan'] = 'English' if lan == 'en-us' else 'Turkish'
    return redirect('home')
