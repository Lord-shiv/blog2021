from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormMixin, FormView
from django.urls import reverse
from django.contrib import messages
from django.db.models import Avg, Count
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
# views 1st one for classbasedview
from hitcount.views import HitCountDetailView
from hitcount.utils import get_hitcount_model
from hitcount.views import HitCountMixin



from .models import Post, Comment, Category
from bootstrap_modal_forms.generic import BSModalCreateView
from .forms import MPTTCommentForm, PostCreateFrom
from users.models import Profile

import datetime


def is_valid_query_param(param):
    return param != '' and param is not None


# def home(request):
#     context = {
#         'posts': Post.objects.all()
#     }
#     return render(request, 'blog/web_home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/web_home.html'  # <apkp>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-created']
    # paginate_by = 4

    def get_context_data(self, **kwargs):
        most_recent = Post.objects.order_by('-created')[:2]
        most_liked = Post.objects.annotate(upVotes_count=Count(
            'upVotes')).order_by('-upVotes_count')[:2]
        most_viewed = Post.objects.order_by('-upVotes')[:2]
        # most_liked_in_last_10_days = Post.objects.annotate(total_likes_in_dt=Count('upVotes', filter=Q(
        #     date_added__lte=time)).filter(total_likes_in_dt__gt=0).order_by('total_likes_in_dt'))[:10]
        # all_tags=Post.tags.all()
        # common_tags=Post.tags.most_common()[:2]
        # similar_posts_by_tags=Post.tags.similar_objects()[:2]

        # most_related = Post.objects.filter(catergory=post.category)
        post_list = Post.objects.all()
        context = super().get_context_data(**kwargs)
        context['post_list'] = post_list
        # context['most_related'] = most_related
        qs = Post.objects.all()
        categories = Category.objects.all()
        title_contains_query = self.request.GET.get('title_contains')
        id_exact_query = self.request.GET.get('id_exact')
        title_or_author_query = self.request.GET.get('title_or_author')
        view_count_min = self.request.GET.get('view_count_min')
        view_count_max = self.request.GET.get('view_count_max')
        date_min = self.request.GET.get('date_min')
        date_max = self.request.GET.get('date_max')
        category = self.request.GET.get('category')
        reviewed = self.request.GET.get('reviewed')
        not_reviewed = self.request.GET.get('notReviewed')

        if is_valid_query_param(title_contains_query):
            qs = qs.filter(title__icontains=title_contains_query)

        elif is_valid_query_param(id_exact_query):
            qs = qs.filter(id=id_exact_query)

        elif is_valid_query_param(title_or_author_query):
            qs = qs.filter(Q(title__icontains=title_or_author_query) |
                           Q(author__name__icontains=title_or_author_query)).distinct()

        if is_valid_query_param(view_count_min):
            qs = qs.filter(views__gte=view_count_min)

        if is_valid_query_param(view_count_max):
            qs = qs.filter(views__lte=view_count_max)

        if is_valid_query_param(date_min):
            qs = qs.filter(publish_date__gte=date_min)

        if is_valid_query_param(date_max):
            qs = qs.filter(publish_date__lte=date_max)

        if is_valid_query_param(category) and category != 'choose..':
            qs = qs.filter(categories__name=category)

        if reviewed == 'on':
            qs = qs.filter(reviewed=True)

        elif not_reviewed == 'on':
            qs = qs.filter(reviewed=False)

        context = {
            'queryset': qs,
            'categories': categories
        }

        return context


class CategoryDetailView(DetailView):
    '''
    Category name: {{ category.name }}
{% for post in category.post_set.all %}
    post: {{ post.title }}
{% endfor %}
    '''
    model = Category
    context_object_name = 'category'
    template_name = 'posts/post_category.html'


@login_required
def like_post(request):
    ''' look at he F expresion for more improvement'''
    if request.POST.get('action') == 'post':
        result = ''
        id_ = int(request.POST.get('postId'))
        post = get_object_or_404(Post, id=id_)
        if post.upVotes.filter(id=request.user.id).exists():
            post.upVotes.remove(request.user)
            post.upVote_count -= 1
            result = post.number_of_upVotes()
            post.save()
        else:
            if post.downVotes.filter(id=request.user.id).exists():
                post.downVotes.remove(request.user)
                post.save()
            post.upVotes.add(request.user)
            post.upVote_count += 1
            result = post.number_of_upVotes()
            post.save()
        return JsonResponse({ 'result': result, 'like_count': post.upVotes.all().count(), 'dislike_count': post.downVotes.all().count() })


@login_required
def dislike_post(request):
    '''similar to like post '''
    if request.POST.get('action') == 'post':
        result = ''
        id_ = int(request.POST.get('postId'))
        post = get_object_or_404(Post, id=id_)
        if post.downVotes.filter(id=request.user.id).exists():
            post.downVotes.remove(request.user)
            post.downVote_count -= 1
            result = post.number_of_downVotes()
            post.save()
        else:
            if post.upVotes.filter(id=request.user.id).exists():
                post.upVotes.remove(request.user)
                post.save()
            post.downVotes.add(request.user)
            post.downVote_count += 1
            result = post.number_of_downVotes()
            post.save()
        return JsonResponse({ 'result': result, 'dislike_count': post.downVotes.all().count(), 'like_count': post.upVotes.all().count() })


# def tagged(request, slug):
#     tag = get_object_or_404(Tag, slug=slug)
#     # Filter posts by tag name
#     posts = Post.objects.filter(tags=tag)
#     context = {
#         'tag':tag,
#         'posts':posts,
#     }
#     return render(request, 'home.html', context)


# class UserPostListView(ListView):
#     model = Post
#     template_name = 'blog/user_posts.html'  # <app>/<model>_<viewtype>.html
#     context_object_name = 'posts'

#     def get_queryset(self, user):
#         user = get_object_or_404(Profile, user=user)
#         return Post.objects.filter(author=user).order_by('-created')


class PostDetailView(FormMixin, HitCountDetailView):
    '''single page with comments, popular post  and similar post'''
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'posts'
    count_hit = True  # view +1
    form_class = MPTTCommentForm

    def get_success_url(self, **kwargs):
        return self.request.path

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(active=True)
        context['comments_form'] = MPTTCommentForm
        context.update({'popular_post': Post.objects.order_by('-hit_count_generic__hits')[:3] })
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        new_comment = form.save(commit=False)
        new_comment.post = self.object
        new_comment.user = self.request.user
        new_comment.save()
        return super().form_valid(form)





# def post_detail_view(request, slug, parent_comment_id=None):
    '''functional view for detail view'''
#     post_detail = get_object_or_404(Post, slug=slug, status='published')
#     comments = post_detail.comments.filter(active=True)
#     comment_form = MPTTCommentForm()

#     if request.method == 'POST':
#         comment_form = MPTTCommentForm(request.POST)
#         if comment_form.is_valid():
#             new_comment = comment_form.save(commit=False)
#             new_comment.post = post_detail
#             if request.user:
#                 new_comment.user = request.user
#                 new_comment.save()
#                 return HttpResponseRedirect(request.path_info)
#             else:
#                 return redirect('login')
#         else:
#             return HttpResponse("please contact the owner")
    
#     context = {
#         'comments_form': comment_form,
#         'comments': comments,
#         'object' : post_detail,
#     }

#     return render(request, 'blog/post_detail.html', context)



def user_posts_view(request, pk):
    user = get_object_or_404(Profile, id=pk)
    posts = Post.objects.filter(author=user).order_by('-created')
    context = {
        'user': user,
        'posts': posts
    }
    return render(request, 'blog/bookmarks.html', context)


class PostCreateView(LoginRequiredMixin, CreateView):
    'success url should be the post user just created.'
    model = Post
    template_name = 'blog/create_blog.html'
    form_class = PostCreateFrom
    success_url = '/'


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'image', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post Updated.')
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    success_message = "Post deleted."

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})


# added for search

def search(request):

    query = request.GET.get('q')
    if query:
        queryset = (Q(title__icontains=query) |
                    Q(image__icontains=query) |
                    Q(author__username__icontains=query) |
                    Q(created__icontains=query) |
                    Q(content__icontains=query))
        results = Post.objects.all().filter(queryset).distinct()
    else:
        results = []
    return render(request, 'blog/search_results.html', {'results': results, 'query': query})
