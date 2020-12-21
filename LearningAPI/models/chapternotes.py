from django.db import models


class ChapterNote(models.Model):
    user = models.ForeignKey("NssUser", on_delete=models.CASCADE)
    markdown_text = models.TextField()
    chapter = models.ForeignKey("BookChapter", on_delete=models.CASCADE)
    public = models.BooleanField()
