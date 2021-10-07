from django.shortcuts import get_object_or_404
from collections import UserList
from django.http.response import HttpResponse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . forms import RegistrationForm, UserForm, LogInForm, UserProfileForm
from blog.models import Post
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib.auth import get_user_model
from . models import Profile


class SignUpView(CreateView):
    form_class = RegistrationForm
    success_url = '/user/login'
    template_name = 'users/register.html'


@login_required
def profile_view(request):
    return render(request,
                  'users/user_profile.html')


class PublicDetailView(DetailView):
    model = Profile
    template_name = 'users/public_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def public_profile(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'users/public_profile.html', {'profile': user})


def followToggle(request, author):
    main_user = request.user
    to_follow = User.objects.get(username=username)
    following = Following.objects.filter(user=main_user, followed=to_follow)
    is_following = True if following else False

    if is_following:
        Following.unfollow(main_user, to_follow)
        is_following = False
    else:
        Following.follow(main_user, to_follow)
        is_following = True
    resp = {
        'following': is_following,
    }

    response = json.dumps(resp)
    return HttpResponse(response, content_type="application/json")


def log_in(request):
    error = False
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        form = LogInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                messages.info(request, f'Welcome back {user.username}!')
                return redirect('/')
            else:
                error = True
    else:
        form = LogInForm()

    return render(request, 'users/login.html', {'form': form, 'error': error})


def log_out(request):
    logout(request)
    return redirect(redirect('/home'))


@login_required
def profile_update_view(request):
    if request.method == 'POST':
        p_form = UserProfileForm(
            request.POST, request.FILES, instance=request.user.profile)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, f'account updated!')
            return redirect('/user/profile')

    else:
        # Todo hide email and private account
        p_form = UserProfileForm(instance=request.user.profile)

    context = {
        'p_form': p_form
    }

    return render(request, 'users/user_profile.html', context)


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, f'logged out.')
    return redirect('/')


# @login_required
# def del_user(request, username):
#     try:
#         if request.method == 'POST':
#             user = User.objects.get(username=username)
#             user.delete()
#             messages.success(request, f"The user is deleted")

#             # TODO might want add confirm view..
#             return redirect('accounts:login')

#     except User.DoesNotExist:
#         messages.error(request, f"User doesn't exist.")
#         return render(request, 'blog/home.html')

@login_required
def bookmarks_list(request):
    bookmarks = Post.objects.filter(bookmarks=request.user)
    context = {
        'bookmarks': bookmarks
    }
    return render(request, 'users/bookmarks.html', context )


@login_required
def remove_saved_bookmark(request, id):
    ''' refresh page after removing bookmarked post '''
    post = get_object_or_404(Post, id=id)
    if post.bookmarks.filter(id=request.user.id).exists():
        post.bookmarks.remove(request.user)
    else:
        post.bookmarks.add(request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
def add_bookmark_detail_page(request):
    ''' bookmark on detailed page '''
    id_ = int(request.POST.get('postId'))
    post = get_object_or_404(Post, id=id_)
    if post.bookmarks.filter(id=request.user.id).exists():
        post.bookmarks.remove(request.user)
    else:
        post.bookmarks.add(request.user)
    return JsonResponse({'bookmark_count': post.bookmarks.all().count()})

@login_required
def add_post_bookmark(request):
    ''' add post to bookmark home page '''
    if request.POST.get('action') == 'post':
        result = ''
        id_ =  request.POST.get('id')
        post = Post.objects.get(id=id_)
        if post.bookmarks.filter(id=request.user.id).exists():
            post.bookmarks.remove(request.user)
            post.save()
            result = post.get_bookmarks_count()
        else:
            post.bookmarks.add(request.user)
            post.save()
            result = post.get_bookmarks_count()

        return JsonResponse({'result': result, 'bookmark_count': post.bookmarks.all().count(), 'post_id': id_})

