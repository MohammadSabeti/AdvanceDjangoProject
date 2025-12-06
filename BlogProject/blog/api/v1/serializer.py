from rest_framework import serializers

from ...models import Post


# ### Approach 1
# class PostSerializer(serializers.Serializer):
#     author = serializers.CharField()
#     title = serializers.CharField(max_length=255)
#     content = serializers.CharField()
#     status = serializers.BooleanField(default=False)

## Approach 2
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['author','title','content','status']
