# In your_app/models.py
from django.db import models

class DocsCategory(models.Model):
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0) # To order categories in the sidebar

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

class DocsTopic(models.Model):
    title = models.CharField(max_length=200)
    # The 'slug' is the URL-friendly version of the title
    # e.g., "MedMinder Overview" -> "medminder-overview"
    slug = models.SlugField(unique=True, help_text="A URL-friendly version of the title.")
    content = models.TextField(help_text="Main content of the topic. Can use HTML or Markdown.")
    category = models.ForeignKey(DocsCategory, on_delete=models.CASCADE, related_name='topics')
    order_in_category = models.PositiveIntegerField(default=0)

    class Meta:
        # This ensures topics are ordered correctly within their category
        ordering = ['category__order', 'order_in_category']

    def __str__(self):
        return self.title