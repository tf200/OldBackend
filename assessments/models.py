import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models


class AssessmentDomain(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name


class Assessment(models.Model):

    class LEVELS(models.IntegerChoices):
        LEVEL_1 = 1, "Level 1"
        LEVEL_2 = 2, "Level 2"
        LEVEL_3 = 3, "Level 3"
        LEVEL_4 = 4, "Level 4"
        LEVEL_5 = 5, "Level 5"

    content = models.TextField(default="", null=True, blank=True)
    domain = models.ForeignKey(
        AssessmentDomain, related_name="assessments", on_delete=models.CASCADE, null=True
    )

    level = models.IntegerField(choices=LEVELS.choices)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def parse_content_as_goals(self) -> list[str]:
        d = ('{"result": %s}' % self.content).replace("'", '"')
        return json.loads(d)["result"]

    class Meta:
        ordering = ("level",)  # Soerting by level is important for Maturity Matrix Table


class MaturityMatrix(models.Model):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="maturity_matrices"
    )

    start_date = models.DateField()
    end_date = models.DateField()

    is_approved = models.BooleanField(default=False)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    assessments = models.ManyToManyField(
        "Assessment",
        through="SelectedMaturityMatrixAssessment",
    )

    class Meta:
        ordering = ("-created",)

    def get_selected_assessments(self) -> list["SelectedMaturityMatrixAssessment"]:
        # raise NotImplementedError(
        #     "'get_selected_assessments' This method should be implemented in the child class."
        # )
        ...


class SelectedMaturityMatrixAssessment(models.Model):
    maturitymatrix = models.ForeignKey(
        MaturityMatrix, related_name="selected_assessments", on_delete=models.CASCADE
    )
    assessment = models.ForeignKey(
        Assessment, related_name="selected_assessments", on_delete=models.CASCADE
    )

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)
