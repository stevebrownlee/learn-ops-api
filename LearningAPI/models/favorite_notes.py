from django.db import models


class FavoriteNote(models.Model):
    user = models.ForeignKey("NssUser", on_delete=models.CASCADE)
    note = models.ForeignKey("ChapterNote", on_delete=models.CASCADE)
