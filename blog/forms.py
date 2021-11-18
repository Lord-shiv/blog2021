from django.db.models import fields
from blog import models
from blog.models import Comment, Post
from django import forms
from mptt.forms import TreeNodeChoiceField


class MPTTCommentForm(forms.ModelForm):
    parent = TreeNodeChoiceField(queryset=Comment.objects.all())
    body = forms.CharField(label='', required=False, min_length=2, max_length=250, widget = forms.Textarea(
        attrs ={
            'class':'form-control ml-1 shadow-none textarea',
            'placeholder':'Tell us what you think about this post..',
            'rows':1,
            'cols': 137
        }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['parent'].widget.attrs.update(
            {'class': 'd-none'})
        self.fields['parent'].label = ''
        self.fields['parent'].required = False


    class Meta:
        model = Comment
        fields = ('body', 'parent')


class PostCreateForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'video', 'status', 'category', 'tags']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['tags'].widget.attrs['placeholder'] = 'e.g car, phone, book..'
        self.fields['title'].widget.attrs['placeholder'] = 'post title here..'
        self.fields['content'].widget.attrs['placeholder'] = 'detailed definition of your post title here.. '