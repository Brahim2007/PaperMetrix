from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Vote, Article


@receiver(post_save, sender=Vote)
def update_article_vote(sender, instance, created, **kwargs):
    article = instance.article
    if created:
        if instance.vote_type == 'up':
            article.upvotes += 1
        else:
            article.downvotes += 1
    else:
        up = Vote.objects.filter(article=article, vote_type='up').count()
        down = Vote.objects.filter(article=article, vote_type='down').count()
        article.upvotes = up
        article.downvotes = down
    article.final_score = article.compute_final_score()
    article.save()


@receiver(post_delete, sender=Vote)
def remove_article_vote(sender, instance, **kwargs):
    article = instance.article
    if instance.vote_type == 'up':
        article.upvotes = max(0, article.upvotes - 1)
    else:
        article.downvotes = max(0, article.downvotes - 1)
    article.final_score = article.compute_final_score()
    article.save()
