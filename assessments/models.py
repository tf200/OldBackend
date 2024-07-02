import json

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
