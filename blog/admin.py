from django.contrib import admin
from .models import Post, Comment

admin.site.register(Post)

# Add Comment with a custom admin class
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created')
    search_fields = ('name', 'email', 'body')