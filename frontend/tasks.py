import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from authorization.models import User
from api.models import Article
from frontend.reccom import get_similar_items
from django.template.loader import render_to_string
from django.db import transaction

logger = logging.getLogger(__name__)

@shared_task
def add():
    for i in User.objects.all():
        if "admin" not in i.email:
            em = i.email
            arts = []
            if i.keywords:
                for i in i.keywords:
                    ids = get_similar_items(query=i,start=0,end=100,get_scores=True)
                    arts.extend(ids)
            if i.tags:
                for i in i.tags:
                    ids = get_similar_items(query=i,start=0,end=100,get_scores=True)
                    arts.extend(ids)
            # rec = [{'title':i.title,'id':i.pk,'score'} for i in Article.objects.filter(pk__in = list(arts))]
            rec = [{'title':Article.objects.get(pk=i[0]).title,'id':i[0],'score':i[-1]} for i in arts]
            rec = sorted(rec,key=lambda c:c['score'],reverse=True)[:10]
            if len(rec) == 0:
                error = 'You have to specify you area of interests first to get recommendations'\

            st = render_to_string('mail_recommendations.html',{'rec':rec})

            send_mail("subject",st, settings.EMAIL_HOST_USER, [em], fail_silently = False,html_message=st)
    return 'ih'


@shared_task
def update_scores():
    """Recompute final scores for all articles if necessary."""
    updated = 0
    with transaction.atomic():
        for article in Article.objects.all():
            new_score = article.compute_final_score()
            if article.final_score != new_score:
                article.final_score = new_score
                article.save()
                updated += 1
    logger.info("Recomputed scores for %s articles", updated)
    return 'updated'


@shared_task
def refresh_tfidf_matrix():
    """Rebuild the cached TF‑IDF matrix used for recommendations."""
    from frontend import reccom
    reccom.rebuild_tfidf_matrix()
    logger.info("TF-IDF matrix rebuilt")
    return 'refreshed'
