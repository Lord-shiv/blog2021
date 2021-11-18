from django.contrib import admin
from .models import Post, Comment, Category

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Category)


# https://django-taggit.readthedocs.io/en/latest/admin.html
# fieldsets = (
#     (None, {'fields': ('tags',)}), tags__name
# )

# class MyModelAdmin(admin.ModelAdmin):
#     list_display = ['tag_list']

#     def get_queryset(self, request):
#         return super().get_queryset(request).prefetch_related('tags')

#     def tag_list(self, obj):
#         return u", ".join(o.name for o in obj.tags.all())
