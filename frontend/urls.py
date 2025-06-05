from django.urls import path
from . import views,get_articles


urlpatterns = [
    path('', views.home,name='home'),
    path('get_article_data/',views.get_article_data,name='get_article_data'),
    path('library/',views.LibaraySet.as_view(),name='library'),
    path('library/<pk>/',views.LibraryDetail.as_view(),name='library_detail'),
    path('recommendation/',views.recomed,name='recommend'),

    path('topics/',views.topics,name='topics'),
    path('add_remove_topic/',views.add_remove_topic,name="add_remove_topic"),
    path('add_or_remove_kw/',views.add_or_remove_kw,name='add_or_remove_kw'),
    path('add_or_remove_author/',views.add_or_remove_author,name='add_or_remove_author'),
    path('author/<pk>/',views.GetAuthor.as_view(),name="get_author"),
    path('load_articles_author/',views.load_articles_author,name='load_articles_author'),
    path('search/',views.search,name='search'),
    path('add_to_library/',views.add_to_library,name='add_to_library'),
    path('delete_library/',views.delete_library,name='delete_library'),

    path('article_api/<str:pk>/',views.DetailArticleAPI.as_view(),name='article_api'),
    path('article/<str:pk>/',views.DetailArticle.as_view(),name='article'),
    path('get_readers/<str:id>/',views.get_readers,name="get_readers"),
    path('update_review/',views.update_review,name='update_review'),
    path('get_recommendation/',views.get_recommendation,name='get_recommendation'),
    path('get_article/',views.get_article,name='get_article'),
    path('get_article_top/',views.get_article_top,name='get_article_top'),
    path('get_article_new/',views.get_article_new,name='get_article_new'),
    path('get_article_trending/',views.get_article_trending,name='get_article_trending'),

    path('get_articles/get_article_from_data/',get_articles.get_article_from_data,name='get_article_from_data'),
    path('get_library_reccomendation/<pk>/',views.get_library_reccomendation,name='get_library_reccomendation'),
    path('smart_recommendations/', views.smart_recommendations, name='smart_recommendations'),

    path('add_tag/<pk>/',get_articles.add_tag,name='add_tag'),
    path('remove_tag/<pk>/',get_articles.remove_tag,name='remove_tag'),

    path('lan/<str:lan>/',views.change_lan),

]
