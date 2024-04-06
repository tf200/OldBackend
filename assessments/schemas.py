from ninja import Schema


class AssessmentLevelSchema(Schema):
    level: int
    assessments: str


class AssessmentDomainSchema(Schema):
    id: int | None = None
    name: str
    levels: list[AssessmentLevelSchema]
