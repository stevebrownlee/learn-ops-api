from django.db import models


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

    @property
    def instructors(self):
        """instructors property, which will be calculated per cohort

        Returns:
            int: Number of instructors per cohort
        """
        try:
            return self.__instructors
        except AttributeError:
            return 0

    @instructors.setter
    def instructors(self, value):
        self.__instructors = value
