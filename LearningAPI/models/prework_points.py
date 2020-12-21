from django.db import models
from . import NssUser


class PreworkPoints(models.Model):
    nss_user = models.ForeignKey(NssUser, on_delete=models.DO_NOTHING)
    javascript = models.IntegerField()
    css = models.IntegerField()
    html = models.IntegerField()
    python = models.IntegerField()
    ruby = models.IntegerField()
    node = models.IntegerField()
    csharp = models.IntegerField()
    other = models.IntegerField()