from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from client.models import ClientDetails, ContractType
from client.schemas import ClientMedicationSchema, ContractTypeSchema
from employees.models import ClientMedication, EmployeeProfile
from system.schemas import EmptyResponseSchema
from system.utils import NinjaCustomPagination

router = Router()


@router.get("/contracts/contract-types", response=list[ContractTypeSchema])
def contract_types(request: HttpRequest):
    return ContractType.objects.all()


@router.post("/contracts/contract-types/add", response={201: ContractTypeSchema})
def add_contract_type(request: HttpRequest, content_type: ContractTypeSchema):
    type = ContractType.objects.create(name=content_type.name)
    if type.id:
        return 201, ContractTypeSchema.from_orm(type)


@router.delete("/contracts/contract-types/{int:id}/delete", response={204: EmptyResponseSchema})
def delete_contract_type(request: HttpRequest, id: int):
    ContractType.objects.filter(id=id).delete()
    return 204, {}


@router.get("/medications", response=list[ClientMedicationSchema])
@paginate(NinjaCustomPagination)
def medications(request: HttpRequest):
    """Return all the medication on the platform"""
    return ClientMedication.objects.all()


@router.get("/medications/{int:client_id}", response=list[ClientMedicationSchema])
@paginate(NinjaCustomPagination)
def client_medications(request: HttpRequest, client_id: int):
    """Returns all the client's medications"""
    return ClientMedication.objects.filter(administered_by=client_id).all()


@router.post("/medications/add", response={201: ClientMedicationSchema})
def add_client_medication(request: HttpRequest, medication: ClientMedicationSchema):
    values = medication.dict()
    client_id = values.pop("client")
    administered_by_id = values.pop("administered_by")

    client = get_object_or_404(ClientDetails, id=client_id)
    administered_by = get_object_or_404(EmployeeProfile, id=administered_by_id)

    client_medication = ClientMedication.objects.create(
        **values, client=client, administered_by=administered_by
    )
    return 201, client_medication
