from django.db import models
from . import NssUser, TreehouseBadge


class NssUserBadge(models.Model):
    nss_user = models.ForeignKey(NssUser, on_delete=models.DO_NOTHING)
    treehouse_badge = models.ForeignKey(TreehouseBadge, on_delete=models.DO_NOTHING)