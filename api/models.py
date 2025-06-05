from django.db import models

from django.contrib.auth import get_user_model
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import json
from django.db.models.signals import post_save, post_delete, pre_save
from django.utils import timezone
import requests
# Create your models here.


class Authors(models.Model):
    name = models.TextField(unique = True)
    done = models.BooleanField()

class Article(models.Model):
    add_on = models.DateTimeField(auto_now_add=True)
    title = models.TextField()
    type = models.TextField()

    authors = models.ManyToManyField(Authors)
    identifiers = models.JSONField()

    keywords = models.JSONField(default=list, null=True, blank=True)

    year = models.IntegerField()
    source = models.TextField()
    publisher = models.TextField()
    id = models.CharField(max_length=50,unique=True,primary_key=True)
    pdf = models.URLField(default=None,null=True,max_length=350)
    link = models.URLField()

    abstract = models.TextField()

    count = models.IntegerField(default=0)
    comm_count = models.IntegerField(default=0)
    score = models.IntegerField(blank=True, null=True)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    deepseek_score = models.FloatField(blank=True, null=True)
    final_score = models.FloatField(blank=True, null=True)
    # reader_count_by_academic_status = models.TextField()
    # reader_count_by_subject_area = models.TextField()
    # reader_count_by_country = models.TextField()

    def get_json(self):
        json_ = {
            "title":self.title,
            "type":self.type,
            "authors":list(self.authors.all().values_list("name",flat=True)),
            "source":self.source,
            "publisher":self.publisher,
            "pdf":self.pdf,
            "link":self.link,
            "abstract":self.abstract
            # "reader_count":self.reader_count,
            # "reader_count_by_academic_status":self.reader_count_by_academic_status,
            # "reader_count_by_subject_area":self.reader_count_by_subject_area,
            # "reader_count_by_country":self.reader_count_by_country
        }
        return json_

    def get_pdf_url(self):
        validator = URLValidator()
        try:
            validator(self.pdf)
            return self.pdf
        except ValidationError:
            if "doi" in self.identifiers: return f"https://dx.doi.org/{self.identifiers['doi']}"
            return "#"

        except AttributeError:
            if "doi" in self.identifiers: return f"https://dx.doi.org/{self.identifiers['doi']}"
            return "#"

    def get_issn(self):
        if "issn" in self.identifiers:
             return f"https://portal.issn.org/api/search?search[]=MUST=allissnbis={self.identifiers['issn'][:4]}-{self.identifiers['issn'][4:]}"

        return None

    def get_doi(self):
        if "doi" in self.identifiers:
             return f"https://dx.doi.org/{self.identifiers['doi']}"

        return None

    def get_total(self):
        count = 0
        for review in self.review_set.all():
            count+=review.rating

        return int(count)

    def get_total_comments(self):
        return len(self.comment_set.all())

    def list_(self):
        return list(self.vote_set.all().values_list('user__email', flat=True))

    def check_up_down(self, user):
        if user.is_authenticated:
            try:
                vote = self.vote_set.get(user=user)
                return 1 if vote.vote_type == 'up' else -1
            except Vote.DoesNotExist:
                pass
        return 0

    def compute_final_score(self):
        today = timezone.now().date()
        age_factor = max(0, 1 - (today - self.add_on.date()).days / 365)
        vote_score = self.upvotes - self.downvotes
        ai_relevance = self.deepseek_score or 0.5
        return round(vote_score * 0.4 + age_factor * 0.2 + ai_relevance * 0.4, 3)

class Review(models.Model):
    rating = models.IntegerField(choices=((-1,-1),(1,1)))
    article = models.ForeignKey(to=Article,on_delete=models.CASCADE)
    user = models.ForeignKey(to=get_user_model(),on_delete=models.CASCADE)


class Vote(models.Model):
    VOTE_TYPES = (
        ('up', 'Upvote'),
        ('down', 'Downvote'),
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    vote_type = models.CharField(choices=VOTE_TYPES, max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')

class Tag(models.Model):
    tag = models.CharField(max_length=50)
    article = models.ManyToManyField(to=Article )
    user = models.ForeignKey(to=get_user_model(),on_delete=models.CASCADE)
    class Meta:
        unique_together = ('user','tag')

def set_total(sender,instance,created,**kwargs):
    article = instance.article
    article.count = article.get_total()
    article.save()
post_save.connect(set_total,sender=Review)

class Library(models.Model):
    name = models.CharField(max_length=20)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    articles = models.ManyToManyField(Article)



class Comment(models.Model):
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    article = models.ForeignKey(Article, models.DO_NOTHING)
    user = models.ForeignKey(get_user_model(), models.DO_NOTHING)
    class Meta:
        ordering = ('-created_on',)

def set_total_comments(sender,instance,created,**kwargs):
    article = instance.article
    article.comm_count = article.get_total_comments()
    article.save()
post_save.connect(set_total_comments,sender=Comment)
def create_alt(sender,instance,**kwargs):
    if instance.identifiers.get('doi') and not instance.score:
        re = requests.get(f'https://api.altmetric.com/v1/doi/{instance.identifiers.get("doi")}')
        if re.ok:
            instance.score = int(re.json()['score'])
        else:
            instance.score = 0
    else:
        instance.score = 0

pre_save.connect(create_alt,sender=Article)

# Import signals to register vote handlers
from . import signals  # noqa
