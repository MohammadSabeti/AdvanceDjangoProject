from django.contrib import admin

from blog.models import Category, Post


# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "status",
        "published_date",
        "created_date",
    )
    list_filter = ("status",)
    search_fields = ["title", "content"]
    empty_value_display = "-empty-"
    date_hierarchy = "published_date"
    actions = ["mark_as_active"]
    save_on_top = True

    def mark_as_active(self, request, queryset):
        queryset.update(status=True)
        self.message_user(
            request, "وضعیت پست های انتخاب شده به وضعیت فعال تغییر پیدا کرد."
        )


admin.site.register(Post, PostAdmin)
admin.site.register(Category)
