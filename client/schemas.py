from ninja import ModelSchema

from client.models import ContractType


class ContractTypeSchema(ModelSchema):
    class Meta:
        model = ContractType
        fields = "__all__"
