from rest_framework import serializers


class PostSerializer(serializers.Serializer):
    author = serializers.CharField()
    title = serializers.CharField(max_length=255)
    content = serializers.CharField()
    status = serializers.BooleanField(default=False)
    published_date = serializers.DateTimeField()
