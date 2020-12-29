from django.db import models


class Cohort(models.Model):
    name = models.CharField(max_length=55)
    slack_channel = models.CharField(max_length=55)
    start_date = models.DateField(auto_now=False, auto_now_add=False)
    end_date = models.DateField(auto_now=False, auto_now_add=False)
    break_start_date = models.DateField(auto_now=False, auto_now_add=False)
    break_end_date = models.DateField(auto_now=False, auto_now_add=False)

    @property
    def students(self):
        """students property, which will be calculated per cohort

        Returns:
            int: Number of students per cohort
        """
        return self.__students

    @students.setter
    def students(self, value):
        self.__students = value

    @property
    def instructors(self):
        """instructors property, which will be calculated per cohort

        Returns:
            int: Number of instructors per cohort
        """
        return self.__instructors

    @instructors.setter
    def instructors(self, value):
        self.__instructors = value