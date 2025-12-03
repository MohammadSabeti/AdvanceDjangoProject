from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializer import PostSerializer
from ...models import Post

@api_view()
def post_list(request):
     posts = Post.objects.all()
     post_serializer = PostSerializer(posts, many=True)
     return Response(post_serializer.data)

@api_view()
def post_detail(request,id):

     try:
          # Approach 1
          post=Post.objects.get(id=id)
          post_serializer=PostSerializer(post)
          return Response(post_serializer.data)
     except Post.DoesNotExist:
          return Response({"detail":"post does not exist :( "},status=status.HTTP_404_NOT_FOUND)

     # # Approach 2

     # post=get_object_or_404(Post,id=id)
     # post_serializer=PostSerializer(post)
     # return Response(post_serializer.data)

