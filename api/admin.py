from django.contrib import admin
from .models import Article, Authors, Vote, Review, Library, Comment


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "publisher", "year", "score", "upvotes", "downvotes", "final_score")
    search_fields = ("title", "publisher")
    list_filter = ("publisher", "year")


admin.site.register(Authors)
@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "vote_type", "created_at")
    search_fields = ("user__email", "article__title")
    list_filter = ("vote_type", "created_at")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "rating")
    search_fields = ("user__email", "article__title")

@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ("name", "user")
    search_fields = ("name", "user__email")

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "created_on")
    search_fields = ("user__email", "article__title")
    readonly_fields = ("created_on",)
