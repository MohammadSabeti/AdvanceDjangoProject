from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from .serializer import PostSerializer
from ...models import Post

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


