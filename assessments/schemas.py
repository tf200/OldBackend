from ninja import Field, ModelSchema, Schema

from assessments.models import AssessmentDomain


class AssessmentLevelSchema(Schema):
    level: int
    assessments: str


class AssessmentDomainSchema(ModelSchema):
    levels: list[AssessmentLevelSchema]

    class Meta:
        model = AssessmentDomain
        fields = "__all__"

    @staticmethod
    def resolve_levels(domain: AssessmentDomain) -> list[AssessmentLevelSchema]:
        return [
            AssessmentLevelSchema(level=assessment.level, assessments=str(assessment.content))
            for assessment in domain.assessments.all()
        ]


class AssessmentDomainInput(ModelSchema):
    levels: list[AssessmentLevelSchema] = []

    class Meta:
        model = AssessmentDomain
        exclude = ("id",)
