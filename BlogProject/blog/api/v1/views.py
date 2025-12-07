from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, GenericAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin,CreateModelMixin
from rest_framework.viewsets import ViewSet, ModelViewSet

from .serializer import PostSerializer
from ...models import Post

# Function Based Views
@api_view(['GET','POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_list(request):
     if request.method=='GET':
          posts = Post.objects.all()
          post_serializer = PostSerializer(posts, many=True)
          return Response(post_serializer.data)
     elif request.method=='POST':
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
@api_view(['GET','PUT','DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_detail(request,id):
     post = get_object_or_404(Post, id=id)
     if request.method=='GET':
          # Approach 1
          # try:
          #      post=Post.objects.get(id=id)
          #      post_serializer=PostSerializer(post)
          #      return Response(post_serializer.data)
          # except Post.DoesNotExist:
          #      return Response({"detail":"post does not exist :( "},status=status.HTTP_404_NOT_FOUND)

          # # Approach 2

          post_serializer=PostSerializer(post)
          return Response(post_serializer.data)
     elif request.method=='PUT':
          serializer=PostSerializer(post,data=request.data)
          serializer.is_valid(raise_exception=True)
          serializer.save()
          return Response(serializer.data)
     elif request.method=='DELETE':
          post.delete()
          return Response({"detail":"post deleted successfully"},status=status.HTTP_204_NO_CONTENT)


# Class Based Views
class PostListAPIView(APIView):
    """
    List all posts, or create a new post.
    """
    permission_classes=[IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer

    def get(self, request):
         """ Retrieving a list of all posts  """
         posts = Post.objects.all()
         post_serializer = self.serializer_class(posts, many=True)
         return Response(post_serializer.data)

    def post(self,request):
         """ Creating a new post with provided data """
         serializer = self.serializer_class(data=request.data)
         serializer.is_valid(raise_exception=True)
         serializer.save()
         return Response(serializer.data)

class PostDetailAPIView(APIView):
    """
    Retrieve, update or delete a post instance.
    """
    permission_classes=[IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer

    def get(self, request,id):
         """ Retrieving a post  """
         post = get_object_or_404(Post, id=id)
         post_serializer = self.serializer_class(post)
         return Response(post_serializer.data)

    def put(self,request,id):
         """ Updating a post  """
         post = get_object_or_404(Post, id=id)
         serializer = self.serializer_class(post, data=request.data)
         serializer.is_valid(raise_exception=True)
         serializer.save()
         return Response(serializer.data)

    def delete(self,request,id):
         """ Deleting a post  """
         post = get_object_or_404(Post, id=id)
         post.delete()
         return Response({"detail": "post deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# Generic Class Based Views

# GenericAPIView,ListModelMixin,CreateModelMixin == ListCreateAPIView
class PostListGenericAPIView(ListCreateAPIView):
     """
     List all posts, or create a new post.
     """
     permission_classes = [IsAuthenticatedOrReadOnly]
     serializer_class = PostSerializer
     queryset = Post.objects.all()

# GenericAPIView,RetrieveModelMixin,UpdateModelMixin,DestroyModelMixin == RetrieveUpdateDestroyAPIView
class PostDetailGenericAPIView(RetrieveUpdateDestroyAPIView):
     """
        Retrieve, update or delete a post instance.
        """
     permission_classes = [IsAuthenticatedOrReadOnly]
     serializer_class = PostSerializer
     queryset = Post.objects.all()
     lookup_field='id'

class PostViewSet(ModelViewSet):
     permission_classes = [IsAuthenticatedOrReadOnly]
     serializer_class = PostSerializer
     queryset = Post.objects.all()


