"""Chapter note class module"""
from django.db import models


class ChapterNote(models.Model):
    """Notes for book chapters"""
    user = models.ForeignKey("NssUser", on_delete=models.CASCADE)
    markdown_text = models.TextField()
    chapter = models.ForeignKey("Chapter", on_delete=models.CASCADE)
    public = models.BooleanField(default=False)
    date = models.DateField(auto_now=True, auto_now_add=False)

    @property
    def votes(self):
        return self.__votes

    @votes.setter
    def votes(self, value):
        self.__votes = value
