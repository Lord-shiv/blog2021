from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required 
from django.contrib.sites.shortcuts import get_current_site
from django.http.response import HttpResponse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.detail import DetailView
from django.views import View
from . forms import RegistrationForm, UserForm, LogInForm, UserProfileForm
from . models import Profile, User
from . utils import account_activation_token
from blog.models import Post
import re
import json
from django.db import transaction


class SignUpView(View):
    def get(self, request):
        return render(request, 'users/register.html')
    @transaction.atomic
    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldValues': request.POST
        }

        if not User.objects.filter(username__iexact=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'Password too short')
                    return render(request, 'users/register.html', context)
                
                user = User.objects.create_user(username=username, email=email, password=password)
                user.set_password(password)
                user.is_active = False
                
                # ------------>
                # Email stuff
                # ------------>
                current_site = get_current_site(request)
                email_subject = 'Activate your account from Sky'
                email_body = {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                }
                link = reverse('users:activate', kwargs={'uidb64': email_body['uid'], 'token': email_body['token']})
                activate_url = 'http://'+current_site.domain+link
                email = EmailMessage(
                    email_subject,
                    'hi '+ user.username + ', greetings from sky community! \n Please click the link below to activate your account. \n' + activate_url,
                    'icanandiwill000@gmail.com',
                    [email],
                )
                email.send(fail_silently=False)
                print(f"user {username} saved!")
                user.save()
                messages.success(request, 'Account successfully created')
                return render(request, 'users/confirm_link.html')
        
        return render(request, 'users/register.html')


class VerificationView(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')
            
            if account_activation_token.check_token(user, token):
                user.is_active = True
                user.save()
                messages.success(request, 'Account activated successfully')
                return redirect('users:login')
            
            if not user.is_active:
                user.is_active = True
        

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
            messages.warning(request, 'The confirmation link was invalid, possibly because it has already been used.')
            return redirect('users:register')


        return redirect('users:login')

class SignIn(View):

    def get(self, request):
        return render(request, 'users/login.html')

    def post(self, request):
        form = LogInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            if email and password:
                user = authenticate(email=email, password=password)
                print('user')
                if user:
                    if user.is_active:
                        login(request, user)
                        messages.info(request, f'Welcome back {user.username}!')
                        return redirect('/')
                    messages.error(request, 'Account is not active,please check your email')
                    return render(request, 'users/login.html')

                messages.error(request, 'Invalid credentials,try again')
                return render(request, 'users/login.html')
            
            messages.error(request, 'Please fill all fields')
            return render(request, 'users/login.html')

        messages.error(request, 'invalid input, Please fill carefully!')
        return render(request, 'users/login.html')


def log_in(request):
    error = False
    if request.method == "POST":
        form = LogInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(email=email, password=password)
            print('user')
            if user:
                login(request, user)
                messages.info(request, f'Welcome {user.username}! ')
                return redirect('/')
            else:
                messages.error(request, 'Invalid credentials,try again')
            return render(request, 'users/login.html')
        else:
            messages.error(request, 'Invalid data')
            return render(request, 'users/login.html')
    else:
        form = LogInForm()

    return render(request, 'users/login.html', {'form': form, 'error': error})


class SignOut(View):
    def post(self, request):
        logout(request)
        messages.success(request, 'logged out')
        return redirect('/')
    
    def get(self, request):
        logout(request)
        messages.success(request, 'logged out')
        return redirect('/')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, f'logged out.')
    return redirect('/')


class UsernameValidation(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']

        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'username already exists'}, status=409)

        if not str(username).isalnum():
            return JsonResponse({'username_error': 'username should only contain alphanumeric characters'}, status=400)
        
        return JsonResponse({'username_valid': True})

class EmailValidation(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']

        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'email already exists'}, status=409)

        if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
            return JsonResponse({'email_error': 'entered email is not a valid email'}, status=400)
        
        return JsonResponse({'email_valid': True})


@login_required
def profile_view(request):
    print('funky one one')
    return render(request, 'users/user_profile.html')


class PublicDetailView(DetailView):
    '''working one'''
    model = Profile
    template_name = 'users/public_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@login_required('login')
def follow_toggle(request):
    '''follow and don't follow user'''
    if request.POST.get('action') == 'post':
        id_ = int(request.POST.get('id'))
        user_profile = get_object_or_404(Profile, id=id_)
        user_followers = user_profile.following.all()
        user = request.user

        if user in user_followers:
            user_profile.following.remove(user)
        user_profile.following.add(user)

        return JsonResponse({'follow_count': user_followers.count()})



def public_profile(request, username):
    print('funky one')
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

