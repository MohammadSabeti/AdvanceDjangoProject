from rest_framework import serializers

from accounts.models import Profile

from ...models import Category, Post

# Approach 1
"""
class PostSerializer(serializers.Serializer):
    author = serializers.CharField()
    title = serializers.CharField(max_length=255)
    content = serializers.CharField()
    status = serializers.BooleanField(default=False)
"""


# Approach 2
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "title",
            "brief_content",
            "content",
            "image",
            "status",
            "category",
            "relative_url",
            "absolute_url",
            "published_date",
        ]
        read_only_fields = ["id", "author"]

    # category = CategorySerializer()
    # better
    category = serializers.SlugRelatedField(
        many=False, slug_field="name", queryset=Category.objects.all()
    )

    author = serializers.SlugRelatedField(read_only=True, slug_field="get_full_name")

    brief_content = serializers.ReadOnlyField(source="first_sentence")
    relative_url = serializers.URLField(source="get_absolute_api_url", read_only=True)
    absolute_url = serializers.SerializerMethodField(
        source="get_absolute_url", read_only=True
    )

    def get_absolute_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.get_absolute_api_url())

    def to_representation(self, instance):
        rep = super(PostSerializer, self).to_representation(instance)
        request = self.context.get("request")
        view = self.context.get("view")

        # separate showing items in list and detail view

        # Approach 1
        """
        if request.parser_context.get('kwargs').get('pk'):
            # detail view
            rep.pop('brief_content', None)
            rep.pop('relative_url', None)
            rep.pop('absolute_url', None)
        else:
            rep.pop('content', None)
        """

        # Approach 2 (better)
        if view and view.action == "list":
            # list view
            rep.pop("content", None)
        else:
            # detail view
            rep.pop("brief_content", None)
            rep.pop("relative_url", None)
            rep.pop("absolute_url", None)

        # separate view and create structure of items by overriding
        rep["category"] = CategorySerializer(
            instance=instance.category, context={"request": request}
        ).data

        return rep

    def create(self, validated_data):
        validated_data["author"] = Profile.objects.get(
            user=self.context["request"].user
        )
        return super(PostSerializer, self).create(validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]
        read_only_fields = ["id"]

    """ # just for test
    def to_representation(self, instance):
        rep=super(CategorySerializer, self).to_representation(instance)
        request = self.context.get('request')
        # separate showing items in list action and get single state
        if request.parser_context.get('kwargs').get('pk'):
            rep['name']=f'#{instance.name}'

        return rep
        """
