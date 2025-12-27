from django.contrib.auth.mixins import (
    LoginRequiredMixin,
)
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.views.generic.base import RedirectView, TemplateView
from .forms import PostForm
from .models import Post

# Create your views here.

# Function Base View show a template
'''
def indexView(request):
    """
    a function based view to show index page
    """
    name = "ali"
    context = {"name":name}
    return render(request,"index.html",context)
'''


class IndexView(TemplateView):
    """
    a class based view to show index page
    """

    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name"] = "mohammad"
        # context["posts"] = Post.objects.all()
        return context


""" FBV for redirect
from django.shortcuts import redirect
def redirectToMaktab(request):
    return redirect('https://maktabkhooneh.com')
"""


class RedirectToMaktab(RedirectView):
    """
    Redirection view sample for maktabkhooneh
    """

    url = "https://maktabkhooneh.com"

    def get_redirect_url(self, *args, **kwargs):
        return super().get_redirect_url(*args, **kwargs)


class PostListView(ListView):
    permission_required = "blog.view_post"
    queryset = Post.objects.all()
    # model = Post
    context_object_name = "posts"
    # paginate_by = 2
    ordering = "-id"
    # def get_queryset(self):
    #     posts = Post.objects.filter(status=True)
    #     return posts


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    # fields = ['author', 'title', 'content','status', 'category', 'published_date']
    form_class = PostForm
    success_url = "/blog/post/"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostEditView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    success_url = "/blog/post/"


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = "/blog/post/"
