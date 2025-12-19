from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import (ListCreateAPIView, GenericAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.mixins import (ListModelMixin, RetrieveModelMixin,
                                   UpdateModelMixin, CreateModelMixin)
from rest_framework.viewsets import ViewSet, ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .permissions import IsOwnerOrReadonly
from .paginations import PostPagination
from .serializer import PostSerializer, CategorySerializer
from ...models import Post, Category
from drf_yasg.utils import swagger_auto_schema

# Function Based Views
@swagger_auto_schema(
    method='get',
    tags=['Blog / Posts (FBV)'],
    operation_summary="List posts",
    operation_description="Retrieve a list of all blog posts"
)
@swagger_auto_schema(
    method='post',
    tags=['Blog / Posts (FBV)'],
    operation_summary="Create post",
    operation_description="Create a new blog post"
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_list(request):
    if request.method == 'GET':
        posts = Post.objects.all()
        post_serializer = PostSerializer(posts, many=True)
        return Response(post_serializer.data)
    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)

        ### Approach 1

        # if serializer.is_valid():
        #      serializer.save()
        #      return Response(serializer.data)
        # else:
        #      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        ### Approach 2

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ordering is required
@swagger_auto_schema(
    methods=['get'],
    tags=['Blog / Posts (FBV)'],
    operation_summary="Retrieve post",
    operation_description="Retrieve a post by its ID"
)
@swagger_auto_schema(
    methods=['put'],
    tags=['Blog / Posts (FBV)'],
    operation_summary="Update post",
    operation_description="Update a post by its ID"
)
@swagger_auto_schema(
    methods=['delete'],
    tags=['Blog / Posts (FBV)'],
    operation_summary="Delete post",
    operation_description="Delete a post by its ID"
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_detail(request, id):
    post = get_object_or_404(Post, id=id)
    if request.method == 'GET':
        # Approach 1
        # try:
        #      post=Post.objects.get(id=id)
        #      post_serializer=PostSerializer(post)
        #      return Response(post_serializer.data)
        # except Post.DoesNotExist:
        #      return Response({"detail":"post does not exist :( "},status=status.HTTP_404_NOT_FOUND)

        # # Approach 2

        post_serializer = PostSerializer(post)
        return Response(post_serializer.data)
    elif request.method == 'PUT':
        serializer = PostSerializer(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        post.delete()
        return Response({"detail": "post deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# Class Based Views
class PostListAPIView(APIView):
    """
    List all posts, or create a new post.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer

    swagger_tags = ["Blog / Posts (APIView)"]
    swagger_summary = {"get": "List posts",
                       "post": "Create post"}
    swagger_description = {
        "get": "Retrieve list of posts using APIView",
        "post": "Create a new post using APIView",
    }
    def get(self, request):
        """ Retrieving a list of all posts  """
        posts = Post.objects.all()
        post_serializer = self.serializer_class(posts, many=True)
        return Response(post_serializer.data)

    def post(self, request):
        """ Creating a new post with provided data """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PostDetailAPIView(APIView):
    """
    Retrieve, update or delete a post instance.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer

    swagger_tags = ["Blog / Posts (APIView)"]
    swagger_summary = {"get": "Retrieve post",
                       "put": "Update post",
                       "delete": "Delete post"}
    swagger_description = {
        "get": "Retrieve a post using APIView",
        "put": "Update a post using APIView",
        "delete": "Delete a post using APIView",
    }
    def get(self, request, id):
        """ Retrieving a post  """
        post = get_object_or_404(Post, id=id)
        post_serializer = self.serializer_class(post)
        return Response(post_serializer.data)

    def put(self, request, id):
        """ Updating a post  """
        post = get_object_or_404(Post, id=id)
        serializer = self.serializer_class(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, id):
        """ Deleting a post  """
        post = get_object_or_404(Post, id=id)
        post.delete()
        return Response({"detail": "post deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# Generic Class Based Views

# GenericAPIView,ListModelMixin,CreateModelMixin == ListCreateAPIView
class PostListGenericAPIView(ListCreateAPIView):

    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    swagger_tags = ["Blog / Posts (ListCreateAPIView)"]
    swagger_summary = {
        "list": "List posts",
        "create": "Create post",
        "get": "List posts",
        "post": "Create post",
    }
    swagger_description = {
        "list": "List posts using generic views",
        "create": "Create post using generic views",
        "get": "List posts using generic views",
        "post": "Create post using generic views",
    }


# (GenericAPIView,RetrieveModelMixin,UpdateModelMixin,
# DestroyModelMixin) == RetrieveUpdateDestroyAPIView
class PostDetailGenericAPIView(RetrieveUpdateDestroyAPIView):

    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    lookup_field = 'id'
    swagger_tags = ["Blog / Posts (RetrieveUpdateDestroyAPIView)"]
    swagger_summary = {
        "retrieve": "Retrieve post",
        "update": "Update post",
        "partial_update": "Partial update post",
        "destroy": "Delete post"
    }

    swagger_description = {
        "retrieve": "Retrieve a post by its ID",
        "update": "Update a post by its ID",
        "partial_update": "Partially update a post",
        "destroy": "Delete a post"
    }



class PostViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadonly]
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ["category","author","status"]
    filterset_fields = {"category": ['exact', 'in'],
                        "author": ['exact'],
                        "status": ['exact']}
    search_fields = ["title", "content"]
    ordering_fields = ["published_date"]
    pagination_class = PostPagination

    swagger_tags = ["Blog / Posts (ModelViewSet)"]
    swagger_summary = {
        "list": "List posts",
        "retrieve": "Retrieve post",
        "create": "Create post",
        "update": "Update post",
        "partial_update": "Partial update post",
        "destroy": "Delete post",
        "get_ok": "Health check",
    }
    swagger_description = {
        "list": "Retrieve a list of all blog posts",
        "retrieve": "Retrieve a post by its ID",
        "create": "Create a new blog post",
        "update": "Update a post by its ID",
        "partial_update": "Partially update a post",
        "destroy": "Delete a post using viewsets",
        "get_ok": "Simple test endpoint",
    }

    @action(methods=['get'], detail=False)
    def get_ok(self, request):
        return Response({'detail': 'ok'})


class CategoryViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    swagger_tags = ['Blog / Categories (ModelViewSet)']
    swagger_summary = {
        "list": "List categories",
        "retrieve": "Retrieve category",
        "create": "Create category",
        "update": "Update category",
        "partial_update": "Partial update category",
        "destroy": "Delete category"
    }
    swagger_description = {
        "list": "Retrieve a list of all blog categories",
        "retrieve": "Retrieve a category by its ID",
        "create": "Create a new category post",
        "update": "Update a category by its ID",
        "partial_update": "Partially update a category",
        "destroy": "Delete a category using viewsets"
    }