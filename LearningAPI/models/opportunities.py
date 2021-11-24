from django.db import models


class Opportunity(models.Model):
    COHORT_PORTIONS = (
        ("CLI", 'Client side'),
        ("SER", 'Server side'),
    )

    senior_instructor = models.ForeignKey(
        "NssUser", on_delete=models.CASCADE, related_name="coaching_opportunities")
    cohort = models.ForeignKey(
        "Cohort", on_delete=models.CASCADE, related_name="ta_opportunities")

    portion = models.CharField(
        max_length=3,
        choices=COHORT_PORTIONS,
        default="CLI",
    )

    start_date = models.DateField(auto_now=False, auto_now_add=False)
    message = models.TextField()
