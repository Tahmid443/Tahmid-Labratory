from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Topic(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(
        blank=True, help_text="Short intro shown on homepage"
    )
    icon = models.CharField(max_length=50, default="📘", help_text="An emoji or icon")
    order = models.IntegerField(default=0, help_text="Lower = appears first")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("lab:topic_detail", kwargs={"slug": self.slug})


class SubTopic(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="subtopics")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    description = models.TextField(
        blank=True, help_text="Short intro for this subtopic page"
    )
    order = models.IntegerField(default=0, help_text="Lower = appears first")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name"]
        unique_together = ("topic", "slug")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.topic.name} → {self.name}"

    def get_absolute_url(self):
        return reverse(
            "lab:subtopic_detail",
            kwargs={
                "topic_slug": self.topic.slug,
                "subtopic_slug": self.slug,
            },
        )


class Section(models.Model):
    subtopic = models.ForeignKey(
        SubTopic, on_delete=models.CASCADE, related_name="sections"
    )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, help_text="Explain the concept")
    code = models.TextField(blank=True, help_text="Code block")
    output = models.TextField(blank=True, help_text="Expected output / result")
    language = models.CharField(
        max_length=50,
        blank=True,
        default="python",
        help_text="Language for syntax label: python, numpy, pandas, sql...",
    )
    order = models.IntegerField(default=0, help_text="Lower = appears first")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.subtopic} — {self.title}"
