from django.db import models
from .nssuser_cohort import NssUserCohort

class Cohort(models.Model):
    """Model for student cohorts"""
    name = models.CharField(max_length=55, unique=True)
    slack_channel = models.CharField(max_length=55, unique=True)
    start_date = models.DateField(auto_now=False, auto_now_add=False)
    end_date = models.DateField(auto_now=False, auto_now_add=False)
    break_start_date = models.DateField(auto_now=False, auto_now_add=False)
    break_end_date = models.DateField(auto_now=False, auto_now_add=False)

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    @property
    def coaches(self):
        coaches = []
        user_cohorts = NssUserCohort.objects.filter(cohort=self, nss_user__user__is_staff=True)
        for user_cohort in user_cohorts:
            coaches.append({
                "id": user_cohort.nss_user.id,
                "name": f'{user_cohort.nss_user}'
            })
        return coaches

    @property
    def is_instructor(self):
        try:
            return self.__is_instructor
        except AttributeError:
            return False

    @is_instructor.setter
    def is_instructor(self, value):
        self.__is_instructor = value



    @property
    def students(self):
        """students property, which will be calculated per cohort

        Returns:
            int: Number of students per cohort
        """
        try:
            return self.__students
        except AttributeError:
            return 0

    @students.setter
    def students(self, value):
        self.__students = value

