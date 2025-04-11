from django.db import models


# Create your models here.
class Post(models.Model):
    # Slug should be a unique field
    slug = models.TextField()
    title = models.TextField()
    published_date = models.DateTimeField()
    last_modified_date = models.DateTimeField(auto_now_add=True)
    mkdwn_content = models.TextField()
