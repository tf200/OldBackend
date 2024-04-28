from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Query, Router
from ninja.pagination import paginate

from assessments.models import AssessmentDomain
from assessments.schemas import AssessmentDomainSchema
from client.models import (
    CarePlan,
    ClientCurrentLevel,
    ClientDetails,
    ClientStatusHistory,
    Contract,
    ContractType,
    ContractWorkingHours,
    DomainGoal,
    DomainObjective,
    GoalHistory,
    Invoice,
    InvoiceHistory,
    ObjectiveHistory,
)
from client.schemas import (
    ClientCurrentLevelInput,
    ClientCurrentLevelPatch,
    ClientCurrentLevelSchema,
    ClientMedicationSchema,
    ClientStatusHistorySchema,
    ContractSchema,
    ContractSchemaInput,
    ContractTypeInput,
    ContractTypeSchema,
    ContractWorkingHoursInput,
    ContractWorkingHoursPatch,
    ContractWorkingHoursSchema,
    DomainGoalInput,
    DomainGoalPatch,
    DomainGoalSchema,
    DomainObjectiveInput,
    DomainObjectivePatch,
    DomainObjectiveSchema,
    GoalHistorySchema,
    InvoiceHistoryInput,
    InvoiceHistorySchema,
    InvoiceSchema,
    InvoiceSchemaPatch,
    MedicationRecordFilterSchema,
    MedicationRecordInput,
    MedicationRecordSchema,
    ObjectiveHistorySchema,
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


@router.get(
    "/contracts/{int:contract_id}/working-hours", response=list[ContractWorkingHoursSchema]
)
@paginate(NinjaCustomPagination)
def contract_working_hours(request: HttpRequest, contract_id: int):
    return ContractWorkingHours.objects.filter(contract__id=contract_id).all()


@router.post("/contracts/{int:contract_id}/working-hours/add", response=ContractWorkingHoursSchema)
def add_contract_working_hours(
    request: HttpRequest, contract_id: int, working_hours: ContractWorkingHoursInput
):
    return ContractWorkingHours.objects.create(contract_id=contract_id, **working_hours.dict())


@router.patch(
    "/contracts/working-hours/{int:id}",
    response=ContractWorkingHoursSchema,
)
def contract_working_hours_details(
    request: HttpRequest, id: int, working_hours: ContractWorkingHoursPatch
):
    ContractWorkingHours.objects.filter(id=id).update(**working_hours.dict(exclude_unset=True))

    return get_object_or_404(ContractWorkingHours, id=id)


@router.delete(
    "/contracts/working-hours/{int:id}/delete",
    response={204: EmptyResponseSchema},
)
def delete_contract_working_hours(request: HttpRequest, id: int):
    ContractWorkingHours.objects.filter(id=id).delete()

    return 204, {}


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


@router.get("/invoices/{int:invoice_id}", response=InvoiceSchema)
def invoice_details(request: HttpRequest, invoice_id: int):
    return get_object_or_404(Invoice, id=invoice_id)


@router.patch("/invoices/{int:invoice_id}/update", response=InvoiceSchema)
def patch_invoices(request: HttpRequest, invoice_id: int, invoice: InvoiceSchemaPatch):
    Invoice.objects.filter(id=invoice_id).update(**invoice.dict(exclude_unset=True))
    invoice: Invoice = get_object_or_404(Invoice, id=invoice_id)
    invoice.refresh_total_amount()
    return invoice


@router.post("/invoices/{int:invoice_id}/history/add", response=InvoiceHistorySchema)
def add_invoice_history_record(
    request: HttpRequest, invoice_id: int, invoice_history: InvoiceHistoryInput
):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    payload = invoice_history.dict()
    # Update the status if the invoice
    if invoice_history.invoice_status:
        invoice.status = invoice_history.invoice_status
        invoice.save()
        del payload["invoice_status"]
    return InvoiceHistory.objects.create(**payload, invoice=invoice)


@router.delete(
    "/invoices/history/{int:record_id}/delete",
    response={204: EmptyResponseSchema},
)
def delete_invoice_history_record(request: HttpRequest, record_id: int):
    InvoiceHistory.objects.filter(id=record_id).delete()
    return 204, {}


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


@router.get("/{int:client_id}/profile-status-history", response=list[ClientStatusHistorySchema])
@paginate(NinjaCustomPagination)
def client_profile_status_history(request: HttpRequest, client_id: int):
    return ClientStatusHistory.objects.filter(client=client_id).all()


@router.get("/{int:client_id}/domains")
def client_domains(request: HttpRequest, client_id: int):
    care_plans = CarePlan.objects.filter(client__id=client_id).all()
    domain_ids: list[int] = []
    for care_plan in care_plans:
        domain_ids.extend([domain.id for domain in care_plan.domains.all()])
    return list(set(domain_ids))


@router.get("/{int:client_id}/domains/{int:domain_id}/goals", response=list[DomainGoalSchema])
@paginate(NinjaCustomPagination)
def client_domain_goals(request: HttpRequest, client_id: int, domain_id: int):
    return DomainGoal.objects.filter(client__id=client_id, domain__id=domain_id).all()


@router.get("/{int:client_id}/goals", response=list[DomainGoalSchema])
@paginate(NinjaCustomPagination)
def client_goals(request: HttpRequest, client_id: int):
    return DomainGoal.objects.filter(client__id=client_id).all()


@router.post("/{int:client_id}/goals/add", response=DomainGoalSchema)
def add_domain_goal(request: HttpRequest, client_id: int, domain_goal: DomainGoalInput):
    return DomainGoal.objects.create(**domain_goal.dict(), client_id=client_id)


@router.delete("/goals/{int:goal_id}/delete", response={204: EmptyResponseSchema})
def delete_domain_goal(request: HttpRequest, goal_id: int):
    DomainGoal.objects.filter(id=goal_id).delete()
    return 204, {}


@router.patch("/goals/{int:goal_id}/update", response={204: EmptyResponseSchema})
def patch_domain_goal(request: HttpRequest, goal_id: int, goal: DomainGoalPatch):
    DomainGoal.objects.filter(id=goal_id).update(**goal.dict(exclude_unset=True))
    return 204, {}


@router.post("/{int:client_id}/goals/{int:goal_id}/objective/add", response=DomainObjectiveSchema)
def add_domain_goal_objective(
    request: HttpRequest, client_id: int, goal_id: int, objective: DomainObjectiveInput
):
    client = get_object_or_404(ClientDetails, id=client_id)
    goal = get_object_or_404(DomainGoal, id=goal_id)
    return DomainObjective.objects.create(**objective.dict(), goal=goal, client=client)


@router.patch("/goals/objective/{int:objective_id}/update", response=DomainObjectiveSchema)
def patch_goal_objective(request: HttpRequest, objective_id: int, objective: DomainObjectivePatch):
    DomainObjective.objects.filter(id=objective_id).update(**objective.dict(exclude_unset=True))
    return get_object_or_404(DomainObjective, id=objective_id)


@router.delete("/goals/objective/{int:objective_id}/delete", response={204: EmptyResponseSchema})
def delete_domain_goal_objective(request: HttpRequest, objective_id: int):
    DomainObjective.objects.filter(id=objective_id).delete()
    return 204, {}


@router.get("/goals/{int:goal_id}/history", response=list[GoalHistorySchema])
@paginate(NinjaCustomPagination)
def goal_history(request: HttpRequest, goal_id: int):
    return GoalHistory.objects.filter(goal__id=goal_id).all()


@router.get("/goals/objectives/{int:objective_id}/history", response=list[ObjectiveHistorySchema])
@paginate(NinjaCustomPagination)
def objective_history(request: HttpRequest, objective_id: int):
    return ObjectiveHistory.objects.filter(objective__id=objective_id).all()


@router.get("/{int:client_id}/current-levels", response=list[ClientCurrentLevelSchema])
def client_current_levels(request: HttpRequest, client_id: int):
    return ClientCurrentLevel.objects.filter(client__id=client_id).all()


@router.post("/{int:client_id}/current-levels/add", response=ClientCurrentLevelSchema)
def add_client_current_levels(
    request: HttpRequest, client_id: int, current_level: ClientCurrentLevelInput
):
    return ClientCurrentLevel.objects.create(**current_level.dict(), client_id=client_id)


@router.patch("/current-levels/{int:current_level_id}/update", response={204: EmptyResponseSchema})
def patch_client_current_levels(
    request: HttpRequest, current_level_id: int, current_level: ClientCurrentLevelPatch
):
    ClientCurrentLevel.objects.filter(id=current_level_id).update(
        **current_level.dict(exclude_unset=True)
    )
    return 204, {}
