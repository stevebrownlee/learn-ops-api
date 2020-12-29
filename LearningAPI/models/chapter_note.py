from django.db import models


class ChapterNote(models.Model):
    user = models.ForeignKey("NssUser", on_delete=models.CASCADE)
    markdown_text = models.TextField()
    chapter = models.ForeignKey("Chapter", on_delete=models.CASCADE)
    public = models.BooleanField(default=False)
    date = models.DateField(auto_now=False, auto_now_add=False)
