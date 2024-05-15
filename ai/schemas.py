from ninja import ModelSchema, Schema

from ai.models import AIGeneratedReport


class ReportSchema(Schema):
    content: str


class AIGeneratedReportSchema(ModelSchema):
    class Meta:
        model = AIGeneratedReport
        fields = "__all__"
