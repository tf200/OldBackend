from ninja import Schema


class AssessmentLevelSchema(Schema):
    level: int
    assessments: str


class AssessmentDomainSchema(Schema):
    name: str
    levels: list[AssessmentLevelSchema]
