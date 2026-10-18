from django.contrib import admin
from .models import Topic, SubTopic, Section


class SectionInline(admin.StackedInline):
    model = Section
    extra = 1
    fields = ("title", "description", "language", "code", "output", "order")


class SubTopicInline(admin.StackedInline):
    model = SubTopic
    extra = 1
    fields = ("name", "slug", "description", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "order", "subtopic_count", "updated_at")
    list_editable = ("order", "icon")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SubTopicInline]

    def subtopic_count(self, obj):
        return obj.subtopics.count()

    subtopic_count.short_description = "Subtopics"


@admin.register(SubTopic)
class SubTopicAdmin(admin.ModelAdmin):
    list_display = ("name", "topic", "order", "section_count", "updated_at")
    list_filter = ("topic",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("order",)
    inlines = [SectionInline]

    def section_count(self, obj):
        return obj.sections.count()

    section_count.short_description = "Sections"


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "subtopic", "language", "order", "updated_at")
    list_filter = ("subtopic__topic", "subtopic", "language")
    search_fields = ("title", "description", "code")
    list_editable = ("order",)
