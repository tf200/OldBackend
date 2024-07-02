from ninja import ModelSchema, Schema

from ai.models import AIGeneratedReport


class ReportSchema(Schema):
    content: str


class AIGeneratedReportSchema(ModelSchema):
    class Meta:
        model = AIGeneratedReport
        fields = "__all__"


class SmartFormulaObjectiveSchema(Schema):
    specific: str
    measurable: str
    achievable: str
    relevant: str
    time_bound: str


class SmartFormulaGoalSchema(Schema):
    goal_name: str
    objectives: list[SmartFormulaObjectiveSchema]


class SmartFormulaResultSchema(Schema):
    goals: list[SmartFormulaGoalSchema]
