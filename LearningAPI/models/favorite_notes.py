from django.db import models


class FavoriteNote(models.Model):
    user = models.ForeignKey("NssUser", on_delete=models.CASCADE, related_name='favorite_notes')
    note = models.ForeignKey("ChapterNote", on_delete=models.CASCADE, related_name='voters')
