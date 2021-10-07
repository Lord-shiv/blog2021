from blog.models import Post
from django.dispatch import receiver
from django.db.models.signals import (
    post_save,
    pre_save,
    pre_delete,
    post_delete,
    m2m_changed
)
from django.utils.text import slugify


@receiver(pre_save, sender=Post)
def blog_slug_post_save(sender, instance, *args, **kwargs):
    '''will create slug right before click save'''
    if not instance.slug:
        instance.slug = slugify(instance.title)


@receiver(pre_delete, sender=Post)
def blog_delete_pre_save(sender, instance, *args, **kwargs):
    print(f"Post with Id {instance.id} - '{instance.title}' has just removed.")


@receiver(post_delete, sender=Post)
def blog_delete_post_save(sender, instance, *args, **kwargs):
    print(f"user with ID {instance.id} has just removed.")


# @receiver(m2m_changed, sender=Post.upVotes.through)
# def blog_like_tracker(sender, instance, action, *args, **kwargs):
#     '''https://www.youtube.com/watch?v=rEX50LJrFuU'''
#     if action == 'pre_add':
#         print("new like")
#         qs = kwargs.get("model").objects.filter(pd__in=kwargs.get('pk_set'))
#         print(qs.count())
