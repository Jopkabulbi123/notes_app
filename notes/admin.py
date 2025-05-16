from django.contrib import admin
from .models import Category, Note

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title',)

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'reminder')
    list_filter = ('category',)
    search_fields = ('title', 'text')