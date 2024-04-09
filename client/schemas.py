from ninja import Field, ModelSchema

from client.models import ClientDetails, ContractType
from employees.models import ClientMedication


class ContractTypeSchema(ModelSchema):
    class Meta:
        model = ContractType
        fields = "__all__"


class ClientDetailsSchema(ModelSchema):
    class Meta:
        model = ClientDetails
        fields = "__all__"


class ClientMedicationSchema(ModelSchema):

    class Meta:
        model = ClientMedication
        fields = "__all__"
        # exclude = ("", "")
        # read_only_fields = ("updated", "created")
