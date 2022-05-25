from django.db import models


# Create your models here.
class SearchResult(models.Model):
    title = models.CharField(max_length=100)
    url = models.URLField('url')
    href = models.URLField('href')
    site = models.CharField(max_length=50)

    def __str__(self):
        return "제목: " + str(self.title) + ", 사진 링크: " + str(self.url) + ", 주소: " + str(self.href) + ", 제공 사이트: " + str(
            self.site)
