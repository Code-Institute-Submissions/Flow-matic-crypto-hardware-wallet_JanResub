from django.shortcuts import render, get_object_or_404, reverse
from django.views import generic, View
from django.views.generic.edit import DeleteView, UpdateView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Post, Comment
from .forms import CommentForm


class PostList(generic.ListView):
    """ Settings frontview of blog """
    model = Post
    queryset = Post.objects.filter(status=1).order_by("-created_on")
    template_name = "about.html"
    paginate_by = 6


class PostDetail(View):
    """ Settings for displaying individual blogposts """

    def get(self, request, slug, *args, **kwargs):
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by("-created_on")
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": False,
                "liked": liked,
                "comment_form": CommentForm()
            },
        )

    def post(self, request, slug, *args, **kwargs):
        """ Send information back to backend """
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by("-created_on")
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment_form.instance.email = request.user.email
            comment_form.instance.name = request.user.username
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
        else:
            comment_form = CommentForm()

        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": True,
                "comment_form": comment_form,
                "liked": liked
            },
        )


class PostLike(View):
    """ A view for handling user likes on a specific post """

    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

        return HttpResponseRedirect(reverse('post_detail', args=[slug]))


class PostDeleteView(DeleteView):
    """
    View for deleting a post if user is the auther of the post
    """
    model = Comment
    template_name = 'comment_delete.html'
    success_url = reverse_lazy('blog')
    success_message = 'Post has been deleted successfully'


class CommentUpdateView(UpdateView):
    """ Update comments """
    model = Comment
    form_class = CommentForm
    template_name = 'comment_update.html'
    success_url = reverse_lazy('home')
    success_message = 'Comment has been updated successfully'

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)
