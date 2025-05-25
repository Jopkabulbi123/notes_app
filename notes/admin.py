from django.contrib import admin
from .models import Category, Note

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('title',)
    date_hierarchy = 'created_at'

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'user', 'created_at')
    list_filter = ('category', 'user')
    search_fields = ('title', 'text')