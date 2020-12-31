from django.db import models


class ChapterNote(models.Model):
    user = models.ForeignKey("NssUser", on_delete=models.CASCADE)
    markdown_text = models.TextField()
    chapter = models.ForeignKey("Chapter", on_delete=models.CASCADE)
    public = models.BooleanField(default=False)
    date = models.DateField(auto_now=True, auto_now_add=False)

    @property
    def favorite_count(self):
        return self.__favorite_count

    @favorite_count.setter
    def favorite_count(self, value):
        self.__favorite_count = value