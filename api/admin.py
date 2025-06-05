from django.contrib import admin
from .models import Article, Authors


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "publisher", "year", "score", "upvotes", "downvotes", "final_score")
    search_fields = ("title", "publisher")
    list_filter = ("publisher", "year")


admin.site.register(Authors)
