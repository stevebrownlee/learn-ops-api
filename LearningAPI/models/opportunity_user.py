from django.db import models


class OpportunityUser(models.Model):
    student = models.ForeignKey(
        "NssUser", on_delete=models.CASCADE, related_name="coaching_opportunities")
    opportunity = models.ForeignKey(
        "Opportunity", on_delete=models.CASCADE, related_name="ta_opportunities")
    date_created = models.DateField(auto_now=True)
