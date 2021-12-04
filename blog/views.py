from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.views.generic.edit import FormMixin, FormView
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.db.models.functions import ExtractDay, ExtractMonth, ExtractQuarter, ExtractWeek, ExtractWeekDay, ExtractIsoYear, ExtractYear, TruncMonth
from django.db.models import Q, F
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from hitcount.views import HitCountDetailView
from hitcount.utils import get_hitcount_model
from hitcount.views import HitCountMixin
from bootstrap_modal_forms.generic import BSModalCreateView
from .forms import MPTTCommentForm, PostCreateForm
from .models import Post, Comment, Category
from users.models import Profile
from taggit.models import Tag
import datetime
import json


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
        most_recent = Post.objects.all().order_by('-created')[:3]
        most_liked = Post.objects.all().annotate(upVotes_count=Count(
            'upVotes')).order_by('-upVotes_count')[:3]
        most_viewed = Post.objects.all().order_by('hit_count_generic')[:3]
        # most_liked_in_last_10_days = Post.objects.annotate(total_likes_in_dt=Count('upVotes', filter=Q(
        #     date_added__lte=time)).filter(total_likes_in_dt__gt=0).order_by('total_likes_in_dt'))[:1]
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
        tags = Tag.objects.all()
       


        context = {
            'queryset': qs,
            'categories': categories,
            'tags': tags,
            'most_recent': most_recent,
            'most_liked': most_liked,
            'most_viewed': most_viewed,
        }

        return context


class CategoryDetailView(DetailView):
    '''
    not using
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
    form_class = PostCreateForm
    success_url = '/'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        form.instance.author = self.request.user.profile
        self.object.save()
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'image', 'category', 'content', 'status', 'tags']
    template_name = 'blog/create_blog.html'
    success_url = "/"

    def dispatch(self, request, *args, **kwargs):
        ''' takes in the request and ultimately returns the response
            middleman between requests and responses.
        '''
        obj = self.get_object()
        if obj.author.id != self.request.user.id:
            raise Http404("you are not allowed to edit this post!")
        return super(PostUpdateView, self).dispatch(request, *args, **kwargs)
    


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    success_message = "Post deleted."

    def test_func(self):
        ''' userPassesTestMi... uses this func'''
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
        
@login_required
def delete_post(request, pk):
    '''this one is in use'''
    post = Post.objects.get(id=pk)
    slug = post.slug
    auth = post.author
    author = str(auth)
    if author == request.user.username:
        post.delete()
        messages.success(request, 'post delete successfully')
        context = {
            'auth': auth
        }
        return redirect('/', context)
    else:
        messages.error(request, 'Unauthorised request.')
        return redirect(f'/post/{slug}'+'/')



def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})


# added for search

def search(request):
    return render(request, 'blog/search_results.html')

# def ajax_search(request):
#     ''' '''
#     if request.is_ajax():
#         print('is json req')
#         res = None
#         posts = request.POST.get('searchText')
#         print(posts)
#         qs = Post.objects.filter(title__icontains=posts)
#         if len(qs) > 0 and len(posts):
#             data = []
#             print(data)
#             for pos in qs:
#                 item = {
#                     'pk': pos.pk,
#                     'name': pos.title,
#                     'author': pos.author,
#                     'category': post.category,
#                     'tags': post.tags,
#                     # 'image': str(pos.image.url)
#                 }
#                 data.append(item)
#             res = data
#         else:
#             res = 'No results found ...'
#         return JsonResponses({'data': posts})
#     print('not json req')
#     return JsonResponse({})
   

def ajax_search(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        authors = Profile.objects.filter(user__username__icontains=search_str).values()
        category = Category.objects.filter(name__icontains=search_str).values()
        tags = Tag.objects.filter(name__icontains=search_str).values()

        all_fields = [f.name for f in Post._meta.get_fields()]  #Post._meta.get_fields()
        '''after this put all_fields in values(*all_fields) the problem is it's giving too much fields '''
        # fields = tuple(x.name for x in Expense._meta.get_fields()) #** tuple **++>> lFI

        if search_str:
            a_results = (Post.objects.filter(
                title__icontains=search_str) | Post.objects.filter(
                created__icontains=search_str) | Post.objects.filter(
                tags__name__contains=search_str) | Post.objects.filter(
                category__name__icontains=search_str) | Post.objects.filter(
                author__user__username__icontains=search_str)).values(author__user__username=F("author__user__username"), content__=F("content"), title__=F('title'),
                                                                        category__name_=F("category__name"), tags__name=F("tags__name"),
                                                                        created_at__month=ExtractMonth('created'), created_at__date=ExtractDay('created'),
                                                                        created_at__year=ExtractYear('created'), slug__ =F("slug"))
            data = list(a_results)
            return JsonResponse(data, safe=False)
        return JsonResponse(data=[], safe=False)
    return JsonResponse(data=[], safe=False)


# if query:
    #         queryset = (Q(title__icontains=query) |
#                     Q(author__username__icontains=query) |
#                     Q(created__icontains=query) |
#                     Q(content__icontains=query))
#         results = Post.objects.all().filter(queryset).distinct()
#     else:
#         results = []
#     return render(request, 'blog/search_results.html', {'results': results, 'query': query})