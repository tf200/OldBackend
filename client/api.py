from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Query, Router
from ninja.pagination import paginate

from client.models import Contract, ContractType, Invoice
from client.schemas import (
    ClientMedicationSchema,
    ContractSchema,
    ContractSchemaInput,
    ContractTypeInput,
    ContractTypeSchema,
    InvoiceSchema,
    MedicationRecordFilterSchema,
    MedicationRecordInput,
    MedicationRecordSchema,
)
from employees.models import ClientMedication, ClientMedicationRecord, EmployeeProfile
from system.schemas import EmptyResponseSchema, ErrorResponseSchema
from system.utils import NinjaCustomPagination

router = Router()


@router.get("/contracts", response=list[ContractSchema])
@paginate(NinjaCustomPagination)
def contracts(request: HttpRequest):
    return Contract.objects.all()


@router.get("/contracts/{int:contract_id}", response=ContractSchema)
def contract_details(request: HttpRequest, contract_id: int):
    return get_object_or_404(Contract, id=contract_id)


@router.get("/{int:client_id}/contracts", response=list[ContractSchema])
@paginate(NinjaCustomPagination)
def client_contracts(request: HttpRequest, client_id: int):
    return Contract.objects.filter(client__id=client_id).all()


@router.post("/contracts/add", response=ContractSchema)
def add_client_contract(request: HttpRequest, contract: ContractSchemaInput):
    return Contract.objects.create(**contract.dict())


@router.put("/contracts/{int:id}/update", response=ContractSchema)
def update_client_contract(request: HttpRequest, id: int, contract: ContractSchemaInput):
    Contract.objects.filter(id=id).update(**contract.dict(exclude_unset=True))

    return get_object_or_404(Contract, id=id)


@router.get("/invoices", response=list[InvoiceSchema])
@paginate(NinjaCustomPagination)
def all_invoices(request: HttpRequest):
    return Invoice.objects.all()


@router.get("/{int:client_id}/invoices", response=list[InvoiceSchema])
@paginate(NinjaCustomPagination)
def client_invoices(request: HttpRequest, client_id: int):
    return Invoice.objects.filter(client__id=client_id).all()


@router.get("/contracts/contract-types", response=list[ContractTypeSchema])
def contract_types(request: HttpRequest):
    return ContractType.objects.all()


@router.post("/contracts/contract-types/add", response={201: ContractTypeSchema})
def add_contract_type(request: HttpRequest, content_type: ContractTypeSchema):
    type = ContractType.objects.create(name=content_type.name)
    if type.id:
        return 201, ContractTypeSchema.from_orm(type)


@router.patch(
    "/contracts/contract-types/{int:contract_type_id}/update", response={204: EmptyResponseSchema}
)
def update_contract_type(
    request: HttpRequest, contract_type_id: int, content_type: ContractTypeInput
):
    ContractType.objects.filter(id=contract_type_id).update(name=content_type.name)
    return 204, {}


@router.delete("/contracts/contract-types/{int:id}/delete", response={204: EmptyResponseSchema})
def delete_contract_type(request: HttpRequest, id: int):
    ContractType.objects.filter(id=id).delete()
    return 204, {}


@router.get("/medications", response=list[ClientMedicationSchema])
@paginate(NinjaCustomPagination)
def medications(request: HttpRequest):
    """Return all the medication on the platform"""
    return ClientMedication.objects.all()


@router.get("/{int:client_id}/medications", response=list[ClientMedicationSchema])
@paginate(NinjaCustomPagination)
def client_medications(request: HttpRequest, client_id: int):
    """Returns all the client's medications"""
    return ClientMedication.objects.filter(client=client_id).all()


@router.post("/medications/add", response={201: ClientMedicationSchema})
def add_client_medication(request: HttpRequest, medication: ClientMedicationSchema):
    client_medication = ClientMedication.objects.create(**medication.dict())

    # Create all medication records at once
    # client_medication.create_medication_records()

    return 201, client_medication


@router.get("/medications/records", response=list[MedicationRecordSchema])
@paginate(NinjaCustomPagination)
def all_medication_records(request: HttpRequest):
    """Return all the records on the platform"""
    return ClientMedicationRecord.objects.all()


@router.get("/medications/{int:medication_id}/records", response=list[MedicationRecordSchema])
@paginate(NinjaCustomPagination)
def medication_records(request: HttpRequest, medication_id: int):
    """Return all the records if a specific medication"""
    medication: ClientMedication = get_object_or_404(ClientMedication, id=medication_id)
    return medication.records.all()  # type: ignore


@router.get(
    "{int:client_id}/medications/records",
    response=list[MedicationRecordSchema],
)
@paginate(NinjaCustomPagination)
def client_medication_records(
    request: HttpRequest, client_id: int, filters: MedicationRecordFilterSchema = Query(...)  # type: ignore
):
    """Return all client's medical records"""
    records = ClientMedicationRecord.objects.filter(client_medication__client=client_id).all()
    records = filters.filter(records)

    return records


@router.get("/medications/records/{int:medication_record_id}", response=MedicationRecordSchema)
def medication_record_details(request: HttpRequest, medication_record_id: int):
    """Return details of a specific medication record"""
    medication_record: ClientMedicationRecord = get_object_or_404(
        ClientMedicationRecord, id=medication_record_id
    )
    return medication_record


@router.patch(
    "/medications/records/{int:medication_record_id}",
    response={200: MedicationRecordSchema, 404: ErrorResponseSchema},
)
def patch_medication_record(
    request: HttpRequest, medication_record_id: int, medication: MedicationRecordInput
):

    if ClientMedicationRecord.objects.filter(id=medication_record_id).update(**medication.dict()):
        return ClientMedicationRecord.objects.get(id=medication_record_id)
    return 404, "Medication Not Found"
