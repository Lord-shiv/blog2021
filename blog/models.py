from django.db import models
from users.models import Profile
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
# image
from django_resized import ResizedImageField
# comments
from mptt.models import MPTTModel, TreeForeignKey
# views
from hitcount.models import HitCountMixin, HitCount
from django.contrib.contenttypes.fields import GenericRelation
# tags
from taggit.managers import TaggableManager


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('post-category', kwargs={'pk': self.pk})


class Post(models.Model):

    options = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    title = models.CharField(max_length=100, null=False, blank=True)
    content = models.TextField(null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    author = models.ForeignKey(
        Profile, on_delete=models.CASCADE)
    video = models.FileField(upload_to='video/', null=True, blank=True)
    slug = models.SlugField(
        max_length=250, unique_for_date='created', blank=True, null=True)
    status = models.CharField(max_length=10, choices=options, default='draft')
    bookmarks = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='bookmark', default=None, blank=True)
    image = ResizedImageField(
        upload_to='images/blog/', quality=75, crop=['middle', 'center'], size=[600, 300], blank=True, null=True)
    hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk',
                                        related_query_name='hit_count_generic_relation')
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, default=1)
    tags = TaggableManager()
    upVotes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='UpVotes')
    downVotes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='DownVotes')
    upVote_count = models.BigIntegerField(default='0')
    downVote_count = models.BigIntegerField(default='0')
    


    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse('post-detail', args=[self.slug])

    def get_category(self):
        return Post.objects.filter(category_id=self.category_id).exclude(pk=self.pk)

    def get_post_author(self):
        return self.author.username

    def upload_image(self, filename):
        return 'post/{}/{}'.format(self.title, filename)

    def number_of_upVotes(self):
        return self.upVotes.count()

    def number_of_downVotes(self):
        return self.downVotes.count()
    
    def get_bookmarks_count(self):
        return self.bookmarks.count()


class Comment(MPTTModel):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,  related_name='replyers')
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='likes')
    dislikes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='dislikes')

    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    class MPTTMeta:
        order_insertion_by = ['created']
    
    class Meta:
        ordering=['tree_id', 'lft']

    def __str__(self):
        return '{} || commented on || "{}" ---->> {}'.format(self.user, self.post.slug, self.body)
