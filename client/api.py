from typing import Any

from django.db import transaction
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Query, Router
from ninja.pagination import paginate

from ai.schemas import EditedSmartFormulaRequestSchema
from assessments.models import Assessment, AssessmentDomain
from client.filters import (
    ClientStateFilter,
    ContractFilterSchema,
    DateFilterSchema,
    InvoiceFilterSchema,
)
from client.models import (
    CarePlan,
    ClientCurrentLevel,
    ClientDetails,
    ClientState,
    ClientStatusHistory,
    CollaborationAgreement,
    ConsentDeclaration,
    ContactRelationship,
    Contract,
    ContractType,
    ContractWorkingHours,
    DataSharingStatement,
    Incident,
    Invoice,
    InvoiceHistory,
    MaturityMatrix,
    RiskAssessment,
    SelectedMaturityMatrixAssessment,
    YouthCareIntake,
)
from client.schemas import (
    ClientCurrentLevelInput,
    ClientCurrentLevelPatch,
    ClientCurrentLevelSchema,
    ClientMedicationSchema,
    ClientStateSchema,
    ClientStateSchemaInput,
    ClientStateSchemaPatch,
    ClientStatusHistorySchema,
    CollaborationAgreementInput,
    CollaborationAgreementSchema,
    ConsentDeclarationInput,
    ConsentDeclarationSchema,
    ContactRelationshipInput,
    ContactRelationshipSchema,
    ContractSchema,
    ContractSchemaInput,
    ContractTypeInput,
    ContractTypeSchema,
    ContractWorkingHoursInput,
    ContractWorkingHoursPatch,
    ContractWorkingHoursSchema,
    DataSharingStatementInput,
    DataSharingStatementSchema,
    DatePeriodSchema,
    DomainGoalInput,
    DomainGoalPatch,
    DomainGoalPatchApproval,
    DomainGoalSchema,
    DomainListSchema,
    DomainObjectiveInput,
    DomainObjectivePatch,
    DomainObjectiveSchema,
    DownloadLinkSchema,
    GoalHistorySchema,
    GPSPositionSchemaInput,
    IncidentInput,
    IncidentPatch,
    IncidentSchema,
    InvoiceHistoryInput,
    InvoiceHistorySchema,
    InvoiceSchema,
    InvoiceSchemaPatch,
    MaturityMatrixInput,
    MaturityMatrixSchema,
    MedicationRecordFilterSchema,
    MedicationRecordInput,
    MedicationRecordSchema,
    ObjectiveHistorySchema,
    ObjectiveHistorySchemaInput,
    ObjectiveHistorySchemaPatch,
    ObjectiveProgressReportSchema,
    RiskAssessmentInput,
    RiskAssessmentSchema,
    SelectedMaturityMatrixAssessmentInput,
    SelectedMaturityMatrixAssessmentSchema,
    YouthCareIntakeInput,
    YouthCareIntakeSchema,
)
from client.utils import get_employee
from employees.models import (
    ClientMedication,
    ClientMedicationRecord,
    DomainGoal,
    DomainObjective,
    GoalHistory,
    ObjectiveHistory,
    ObjectiveProgressReport,
)
from system.schemas import EmptyResponseSchema, ErrorResponseSchema
from system.utils import NinjaCustomPagination

router = Router()


@router.get("/contracts", response=list[ContractSchema])
@paginate(NinjaCustomPagination)
def contracts(request: HttpRequest, filter: ContractFilterSchema = Query(...)):  # type: ignore
    return filter.filter(Contract.objects.all())


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
    if contract.hours is None:
        contract.hours = 0
    return Contract.objects.create(**contract.dict())


@router.put("/contracts/{int:id}/update", response=ContractSchema)
def update_client_contract(request: HttpRequest, id: int, contract: ContractSchemaInput):
    Contract.objects.filter(id=id).update(**contract.dict(exclude_unset=True))

    return get_object_or_404(Contract, id=id)


@router.get("/invoices", response=list[InvoiceSchema])
@paginate(NinjaCustomPagination)
def all_invoices(request: HttpRequest, filter: InvoiceFilterSchema = Query(...)):  # type: ignore
    return filter.filter(Invoice.objects.all())


@router.get("/invoices/{int:invoice_id}", response=InvoiceSchema)
def invoice_details(request: HttpRequest, invoice_id: int):
    return get_object_or_404(Invoice, id=invoice_id)


@router.get("/invoices/{int:invoice_id}/download-link", response=DownloadLinkSchema)
def invoice_download_as_pdf(request: HttpRequest, invoice_id: int):
    """Download invoice as PDF"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return {"download_link": invoice.download_link()}


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
    created_by = get_employee(request.user)  # Get Employee profile
    return DomainGoal.objects.create(
        **domain_goal.dict(), client_id=client_id, created_by=created_by
    )


@router.delete("/goals/{int:goal_id}/delete", response={204: EmptyResponseSchema})
def delete_domain_goal(request: HttpRequest, goal_id: int):
    DomainGoal.objects.filter(id=goal_id).delete()
    return 204, {}


@router.patch("/goals/{int:goal_id}/update", response={204: EmptyResponseSchema})
def patch_domain_goal(request: HttpRequest, goal_id: int, goal: DomainGoalPatch):
    DomainGoal.objects.filter(id=goal_id).update(**goal.dict(exclude_unset=True))
    return 204, {}


@router.patch("/goals/{int:goal_id}/approval", response={204: EmptyResponseSchema})
def domain_goal_approval(request: HttpRequest, goal_id: int):
    reviewed_by = get_employee(request.user)

    DomainGoal.objects.filter(id=goal_id).update(is_approved=True, reviewed_by=reviewed_by)
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
def goal_history(request: HttpRequest, goal_id: int, filter: DateFilterSchema = Query(...)):  # type: ignore
    return filter.filter(GoalHistory.objects.filter(goal__id=goal_id).all())


@router.get("/goals/objectives/{int:objective_id}/history", response=list[ObjectiveHistorySchema])
def objective_history(request: HttpRequest, objective_id: int, filter: DateFilterSchema = Query(...)):  # type: ignore
    return filter.filter(ObjectiveHistory.objects.filter(objective__id=objective_id).all())


@router.post("/goals/objectives/{int:objective_id}/history/add", response=ObjectiveHistorySchema)
def add_objective_history(
    request: HttpRequest, objective_id: int, objective_history: ObjectiveHistorySchemaInput
):
    return ObjectiveHistory.objects.create(**objective_history.dict(), objective_id=objective_id)


@router.patch("/goals/objectives/history/{int:history_id}/update", response=ObjectiveHistorySchema)
def patch_objective_history(
    request: HttpRequest, history_id: int, objective_history: ObjectiveHistorySchemaPatch
):
    ObjectiveHistory.objects.filter(id=history_id).update(
        **objective_history.dict(exclude_unset=True)
    )

    return get_object_or_404(ObjectiveHistory, id=history_id)


@router.delete(
    "/goals/objectives/history/{int:history_id}/delete", response={204: EmptyResponseSchema}
)
def delete_objective_history(request: HttpRequest, history_id: int):
    ObjectiveHistory.objects.filter(id=history_id).delete()
    return 204, {}


@router.get("/{int:client_id}/current-levels", response=list[ClientCurrentLevelSchema])
def client_current_levels(request: HttpRequest, client_id: int):
    # get client domains
    client = get_object_or_404(ClientDetails, id=client_id)
    domain_ids: list[int] = client.get_domain_ids()
    # fetch latest domain levels
    domain_levels = []
    for domain_id in domain_ids:
        level = (
            ClientCurrentLevel.objects.filter(domain__id=domain_id, client__id=client_id)
            .order_by("-created")
            .first()
        )
        if level:
            domain_levels.append(level)

    return [ClientCurrentLevelSchema.from_orm(domain_level) for domain_level in domain_levels]


@router.get("/{int:client_id}/levels", response=list[ClientCurrentLevelSchema])
def client_levels_history(request: HttpRequest, client_id: int):
    return ClientCurrentLevel.objects.filter(client__id=client_id).all()


@router.post("/{int:client_id}/levels/add", response=ClientCurrentLevelSchema)
def add_client_current_levels(
    request: HttpRequest, client_id: int, current_level: ClientCurrentLevelInput
):
    return ClientCurrentLevel.objects.create(**current_level.dict(), client_id=client_id)


@router.patch("/levels/{int:level_id}/update", response={204: EmptyResponseSchema})
def patch_client_current_levels(
    request: HttpRequest, level_id: int, current_level: ClientCurrentLevelPatch
):
    ClientCurrentLevel.objects.filter(id=level_id).update(**current_level.dict(exclude_unset=True))
    return 204, {}


@router.get("/{int:client_id}/states", response=list[ClientStateSchema])
@paginate(NinjaCustomPagination)
def client_states(request: HttpRequest, client_id: int, filters: ClientStateFilter = Query()):  # type: ignore
    client = get_object_or_404(ClientDetails, id=client_id)
    return filters.filter(client.client_states.all())  # type: ignore


@router.post("/states/add", response=ClientStateSchema)
def add_client_states(request: HttpRequest, client_state: ClientStateSchemaInput):
    return ClientState.objects.create(**client_state.dict(exclude_unset=True))


@router.patch("/states/{int:state_id}/update", response=ClientStateSchema)
def patch_client_states(request: HttpRequest, state_id: int, client_state: ClientStateSchemaPatch):
    ClientState.objects.filter(id=state_id).update(**client_state.dict(exclude_unset=True))
    return get_object_or_404(ClientState, id=state_id)


@router.delete("/states/{int:state_id}/delete", response={204: EmptyResponseSchema})
def delete_client_states(request: HttpRequest, state_id: int):
    ClientState.objects.filter(id=state_id).delete()
    return 204, {}


@router.post("/{int:client_id}/gps/update", response={204: EmptyResponseSchema})
def update_client_gps_location(
    request: HttpRequest, client_id: int, gps_position: GPSPositionSchemaInput
):
    ClientDetails.objects.filter(id=client_id).update(
        gps_position=[gps_position.latitude, gps_position.longitude]
    )
    return 204, {}


@router.get("/emergency-contacts/contact-relationships", response=list[ContactRelationshipSchema])
def contact_relationships(request: HttpRequest):
    return ContactRelationship.objects.filter(soft_delete=False).all()


@router.post("/emergency-contacts/contact-relationships/add", response=ContactRelationshipSchema)
def add_contact_relationships(request: HttpRequest, relationship: ContactRelationshipInput):
    return ContactRelationship.objects.create(**relationship.dict())


@router.delete(
    "/emergency-contacts/contact-relationships/{int:id}/delete",
    response={204: EmptyResponseSchema},
)
def delete_contact_relationships(request: HttpRequest, id: int):
    ContactRelationship.objects.filter(id=id).update(soft_delete=True)
    return 204, {}


@router.get("/incidents", response=list[IncidentSchema])
@paginate(NinjaCustomPagination)
def get_all_incidents(request: HttpRequest):
    return Incident.objects.filter(soft_delete=False).all()


@router.get("/{int:client_id}/incidents", response=list[IncidentSchema])
@paginate(NinjaCustomPagination)
def get_client_incidents(request: HttpRequest, client_id: int):
    return Incident.objects.filter(client__id=client_id, soft_delete=False).all()


@router.post("/incidents/add", response=IncidentSchema)
def add_incident(request: HttpRequest, incident: IncidentInput):
    return Incident.objects.create(**incident.dict())


@router.post("/incidents/{int:incident_id}/update", response=IncidentSchema)
def edit_incident(request: HttpRequest, incident_id: int, incident: IncidentPatch):
    Incident.objects.filter(id=incident_id).update(**incident.dict(exclude_unset=True))
    return get_object_or_404(Incident, id=incident_id)


@router.get("/incidents/{int:incident_id}/details", response=IncidentSchema, auth=None)
def incident_details(request: HttpRequest, incident_id: int):
    return get_object_or_404(Incident, id=incident_id)


@router.delete("/incidents/{int:incident_id}/delete", response={204: EmptyResponseSchema})
def delete_incident(request: HttpRequest, incident_id: int):
    Incident.objects.filter(id=incident_id).update(soft_delete=True)
    return 204, {}


@router.get(
    "/{int:client_id}/questionnairs/collaboration_agreements",
    response=list[CollaborationAgreementSchema],
    tags=["questionnairs"],
)
@paginate(NinjaCustomPagination)
def get_collaboration_agreement(request: HttpRequest, client_id: int):
    return CollaborationAgreement.objects.filter(client__id=client_id).all()


@router.post(
    "/questionnairs/collaboration_agreements/add",
    response=CollaborationAgreementSchema,
    tags=["questionnairs"],
)
def add_collaboration_agreement(request: HttpRequest, payload: CollaborationAgreementInput):
    return CollaborationAgreement.objects.create(**payload.dict())


@router.post(
    "/questionnairs/collaboration_agreements/{int:agreement_id}/update",
    response=CollaborationAgreementSchema,
    tags=["questionnairs"],
)
def update_collaboration_agreement(
    request: HttpRequest, agreement_id: int, payload: CollaborationAgreementInput
):
    CollaborationAgreement.objects.filter(id=agreement_id).update(
        **payload.dict(exclude_unset=True)
    )
    return get_object_or_404(CollaborationAgreement, id=agreement_id)


@router.get(
    "/questionnairs/collaboration_agreements/{int:agreement_id}/details",
    response=CollaborationAgreementSchema,
    tags=["questionnairs"],
)
def collaboration_agreement_details(request: HttpRequest, agreement_id: int):
    return get_object_or_404(CollaborationAgreement, id=agreement_id)


@router.delete(
    "/questionnairs/collaboration_agreements/{int:agreement_id}/delete",
    response={204: EmptyResponseSchema},
    tags=["questionnairs"],
)
def delete_collaboration_agreement(request: HttpRequest, agreement_id: int):
    CollaborationAgreement.objects.filter(id=agreement_id).delete()
    return 204, {}


@router.get(
    "/questionnairs/risk-assessments", response=list[RiskAssessmentSchema], tags=["questionnairs"]
)
@paginate(NinjaCustomPagination)
def get_risk_assessments(request: HttpRequest):
    return RiskAssessment.objects.all()


@router.get(
    "/{int:client_id}/questionnairs/risk-assessments",
    response=list[RiskAssessmentSchema],
    tags=["questionnairs"],
)
@paginate(NinjaCustomPagination)
def get_client_risk_assessments(request: HttpRequest, client_id: int):
    return RiskAssessment.objects.filter(client__id=client_id).all()


@router.post(
    "/questionnairs/risk-assessments/add",
    response=RiskAssessmentSchema,
    tags=["questionnairs"],
)
def add_risk_assessments(request: HttpRequest, payload: RiskAssessmentInput):
    return RiskAssessment.objects.create(**payload.dict())


@router.post(
    "/questionnairs/risk-assessments/{int:risk_assessment_id}/update",
    response=RiskAssessmentSchema,
    tags=["questionnairs"],
)
def update_risk_assessments(
    request: HttpRequest, risk_assessment_id: int, payload: RiskAssessmentInput
):
    RiskAssessment.objects.filter(id=risk_assessment_id).update(**payload.dict())
    return get_object_or_404(RiskAssessment, id=risk_assessment_id)


@router.get(
    "/questionnairs/risk-assessments/{int:risk_assessment_id}/details",
    response=RiskAssessmentSchema,
    tags=["questionnairs"],
)
def risk_assessments_details(request: HttpRequest, risk_assessment_id: int):
    return get_object_or_404(RiskAssessment, id=risk_assessment_id)


@router.delete(
    "/questionnairs/risk-assessments/{int:risk_assessment_id}/delete",
    response={204: EmptyResponseSchema},
    tags=["questionnairs"],
)
def delete_risk_assessment(request: HttpRequest, risk_assessment_id: int):
    RiskAssessment.objects.filter(id=risk_assessment_id).delete()
    return 204, {}


@router.get(
    "/{int:client_id}/questionnairs/consent-declarations",
    response=list[ConsentDeclarationSchema],
    tags=["questionnairs"],
)
@paginate(NinjaCustomPagination)
def get_concent_declarations(request: HttpRequest, client_id: int):
    return ConsentDeclaration.objects.filter(client__id=client_id).all()


# create endpoints for the consent declarations
@router.post(
    "/questionnairs/consent-declarations",
    response=ConsentDeclarationSchema,
    tags=["questionnairs"],
)
def add_consent_declaration(request: HttpRequest, payload: ConsentDeclarationInput):
    return ConsentDeclaration.objects.create(**payload.dict())


# The details endpoint
@router.get(
    "/questionnairs/consent-declarations/{int:consent_declaration_id}/details",
    response=ConsentDeclarationSchema,
    tags=["questionnairs"],
)
def consent_declaration_details(request: HttpRequest, consent_declaration_id: int):
    return get_object_or_404(ConsentDeclaration, id=consent_declaration_id)


# The update endpoint
@router.post(
    "/questionnairs/consent-declarations/{int:consent_declaration_id}/update",
    response=ConsentDeclarationSchema,
    tags=["questionnairs"],
)
def update_consent_declaration(
    request: HttpRequest, consent_declaration_id: int, payload: ConsentDeclarationInput
):
    ConsentDeclaration.objects.filter(id=consent_declaration_id).update(**payload.dict())
    return get_object_or_404(ConsentDeclaration, id=consent_declaration_id)


# The delete endpoint
@router.delete(
    "/questionnairs/consent-declarations/{int:consent_declaration_id}/delete",
    response={204: EmptyResponseSchema},
    tags=["questionnairs"],
)
def delete_consent_declaration(request: HttpRequest, consent_declaration_id: int):
    ConsentDeclaration.objects.filter(id=consent_declaration_id).delete()
    return 204, {}


# Questionnaire YouthCareIntake CRUD
@router.get(
    "/{int:client_id}/questionnairs/youth-care-intakes",
    response=list[YouthCareIntakeSchema],
    tags=["questionnairs"],
)
@paginate(NinjaCustomPagination)
def get_youth_care_intakes(request: HttpRequest, client_id: int):
    return YouthCareIntake.objects.filter(client__id=client_id).all()


@router.post(
    "/questionnairs/youth-care-intakes/add",
    response=YouthCareIntakeSchema,
    tags=["questionnairs"],
)
def add_youth_care_intake(request: HttpRequest, payload: YouthCareIntakeInput):
    return YouthCareIntake.objects.create(**payload.dict())


@router.get(
    "/questionnairs/youth-care-intakes/{int:intake_id}/details",
    response=YouthCareIntakeSchema,
    tags=["questionnairs"],
)
def get_youth_care_intake(request: HttpRequest, intake_id: int):
    return get_object_or_404(YouthCareIntake, id=intake_id)


@router.post(
    "/questionnairs/youth-care-intakes/{int:intake_id}/update",
    response=YouthCareIntakeSchema,
    tags=["questionnairs"],
)
def update_youth_care_intake(request: HttpRequest, intake_id: int, payload: YouthCareIntakeInput):
    YouthCareIntake.objects.filter(id=intake_id).update(**payload.dict())
    return get_object_or_404(YouthCareIntake, id=intake_id)


@router.delete(
    "/questionnairs/youth-care-intakes/{int:intake_id}/delete",
    response={204: EmptyResponseSchema},
    tags=["questionnairs"],
)
def delete_youth_care_intake(request: HttpRequest, intake_id: int):
    YouthCareIntake.objects.filter(id=intake_id).delete()
    return 204, {}


# Creating the crud for DataSharingStatement
@router.get(
    "/{int:client_id}/questionnairs/data-sharing-statements",
    response=list[DataSharingStatementSchema],
    tags=["questionnairs"],
)
@paginate(NinjaCustomPagination)
def get_data_sharing_statements(request: HttpRequest, client_id: int):
    return DataSharingStatement.objects.filter(client__id=client_id).all()


@router.get(
    "/questionnairs/data-sharing-statements/{int:statement_id}/details",
    response=DataSharingStatementSchema,
    tags=["questionnairs"],
)
def get_data_sharing_statement(request: HttpRequest, statement_id: int):
    return get_object_or_404(DataSharingStatement, id=statement_id)


@router.post(
    "/questionnairs/data-sharing-statements/add",
    response=DataSharingStatementSchema,
    tags=["questionnairs"],
)
def add_data_sharing_statement(request: HttpRequest, payload: DataSharingStatementInput):
    return DataSharingStatement.objects.create(**payload.dict())


@router.post(
    "/questionnairs/data-sharing-statements/{int:statement_id}/update",
    response=DataSharingStatementSchema,
    tags=["questionnairs"],
)
def update_data_sharing_statement(
    request: HttpRequest, statement_id: int, payload: DataSharingStatementInput
):
    DataSharingStatement.objects.filter(id=statement_id).update(**payload.dict())
    return get_object_or_404(DataSharingStatement, id=statement_id)


@router.delete(
    "/questionnairs/data-sharing-statements/{int:statement_id}/delete",
    response={204: EmptyResponseSchema},
    tags=["questionnairs"],
)
def delete_data_sharing_statement(request: HttpRequest, statement_id: int):
    DataSharingStatement.objects.filter(id=statement_id).delete()
    return 204, {}


# Objective progress report CRUD
@router.get(
    "/objectives/{int:objective_id}/progress-reports",
    response=list[ObjectiveProgressReportSchema],
)
@paginate(NinjaCustomPagination)
def get_objective_progress_reports(request: HttpRequest, objective_id: int):
    return ObjectiveProgressReport.objects.filter(objective__id=objective_id).all()


@router.delete(
    "/objectives/progress-reports/{int:report_id}/delete",
    response={204: EmptyResponseSchema},
)
def delete_objective_progress_report(request: HttpRequest, report_id: int):
    ObjectiveProgressReport.objects.filter(id=report_id).delete()
    return 204, {}


@router.post("/{int:client_id}/selected-domains/update", response={204: EmptyResponseSchema})
def save_client_maturity_matrix_domains(
    request: HttpRequest, client_id: int, domains: DomainListSchema
):
    client = get_object_or_404(ClientDetails, id=client_id)

    client.maturity_domains = domains.domains
    client.save()

    return 204, {}


@router.get("/{int:client_id}/selected-domains", response=DomainListSchema)
def get_client_domains(request: HttpRequest, client_id: int):
    client = get_object_or_404(ClientDetails, id=client_id)
    return {"domains": client.get_selected_domains()}


@router.post(
    "/{int:client_id}/smart-formula/{int:goal_id}/{int:level_id}/add",
    response=list[int],  # DomainGoal ids
)
def save_smart_formula_result(
    request: HttpRequest,
    client_id: int,
    goal_id: int,
    level_id: int,
    result: EditedSmartFormulaRequestSchema,
):
    # Create domain goals and objectives from smart formula result
    client = get_object_or_404(ClientDetails, id=client_id)
    domain = get_object_or_404(AssessmentDomain, id=goal_id)
    assessment = get_object_or_404(Assessment, domain=domain, level=level_id)

    domain_goal_ids: list[int] = []

    if client and domain and assessment:
        # Start DB transaction
        with transaction.atomic():
            for smart_goal in result.goals:
                # Create DomainObjective
                goal = DomainGoal.objects.create(
                    client=client,
                    domain=domain,
                    title=smart_goal.title,
                    desc="",
                )

                domain_goal_ids.append(goal.pk)

                # Create objectives and asign them to the goal
                for smart_objective in smart_goal.objectives:
                    objective = DomainObjective.objects.create(
                        client=client,
                        goal=goal,
                        title=smart_objective.title,
                        desc=smart_objective.description,
                    )
                    goal.objectives.add(objective)  # type: ignore
                    goal.save()  # just in case

    return domain_goal_ids


@router.get(
    "/{int:client_id}/smart-formula/{int:goal_id}/{int:level_id}",
    response=EditedSmartFormulaRequestSchema,
)
def get_smart_formula(request: HttpRequest, client_id: int, goal_id: int, level_id: int):
    client = get_object_or_404(ClientDetails, id=client_id)
    domain = get_object_or_404(AssessmentDomain, id=goal_id)
    assessment = get_object_or_404(Assessment, domain=domain, level=level_id)
    # goals = DomainGoal.objects.filter(client=client, domain=domain).all()

    return {
        "goals": [
            {
                "title": goal.title,
                "objectives": [
                    {"title": objective.title, "description": objective.desc}
                    for objective in goal.objectives.all()
                ],
            }
            for goal in domain.goals.filter(client=client).all()
        ]
    }


# @router.get(
#     "/{int:client_id}/smart-formula",
#     response=EditedSmartFormulaRequestSchema,
# )
# def get_smart_formula(request: HttpRequest, client_id: int):
#     client = get_object_or_404(ClientDetails, id=client_id)
#     domains = AssessmentDomain.objects.filter(client=client).all()

#     for domain in domains:
#         assessment = get_object_or_404(Assessment, domain=domain)

#     return {
#         "goals": [
#             {
#                 "title": goal.title,
#                 "objectives": [
#                     {"title": objective.title, "description": objective.desc}
#                     for objective in goal.objectives.all()
#                 ],
#             }
#             for goal in domain.goals.all()
#         ]
#     }


@router.get(
    "/{int:client_id}/questionnaires/maturity-matrices",
    response=list[MaturityMatrixSchema],
    tags=["questionnairs"],
)
def get_client_maturity_matries(request: HttpRequest, client_id: int):
    client = get_object_or_404(ClientDetails, id=client_id)
    # return client.get_maturity_matrices()
    # Get All the matrices for the client
    return MaturityMatrix.objects.filter(client=client).all()


@router.get(
    "/questionnaires/maturity-matrices/{matrix_id}/details",
    response=MaturityMatrixSchema,
    tags=["questionnairs"],
)
def get_client_maturity_matrix_details(request: HttpRequest, matrix_id: int):
    # Get All the matrices for the client
    return get_object_or_404(MaturityMatrix, id=matrix_id)


@router.post(
    "/questionnaires/maturity-matrices/add",
    response=MaturityMatrixSchema,
    tags=["questionnairs"],
)
def add_maturity_matrix(request: HttpRequest, payload: MaturityMatrixInput):
    client_id = payload.client_id
    client = get_object_or_404(ClientDetails, id=client_id)

    maturity_matrix = MaturityMatrix.objects.create(
        client=client,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )

    # Create Selected Maturity Matrix Assessment for each goal
    for assessment_payload in payload.maturity_matrix:
        domain = get_object_or_404(AssessmentDomain, id=assessment_payload.domain_id)
        assessment = get_object_or_404(Assessment, domain=domain, level=assessment_payload.level)
        if domain and assessment:
            selected_assessment = SelectedMaturityMatrixAssessment.objects.create(
                maturitymatrix=maturity_matrix, assessment=assessment
            )
            # Update the goal with the selected assessment
            DomainGoal.objects.filter(id__in=assessment_payload.goal_ids).update(
                selected_maturity_matrix_assessment=selected_assessment
            )

    return maturity_matrix


@router.post(
    "/questionnaires/maturity-matrices/selected-assessments/add",
    response=SelectedMaturityMatrixAssessmentSchema,
    tags=["questionnairs"],
)
def add_selected_assessment(
    request: HttpRequest,
    payload: SelectedMaturityMatrixAssessmentInput,
):
    print(payload.model_dump())

    matrix = get_object_or_404(MaturityMatrix, id=payload.maturitymatrix_id)
    assessment = get_object_or_404(Assessment, id=payload.assessment_id)

    # let's create the selected maturity matrix
    return SelectedMaturityMatrixAssessment.objects.create(
        maturitymatrix=matrix, assessment=assessment
    )


# @router.get(
#     "/questionnaires/maturity-matrices/selected-assessments/{int:domain_id}/{int:level}",
#     response=SelectedMaturityMatrixAssessmentSchema,
#     tags=["questionnairs"],
# )
# def get_client_selected_assessment(request: HttpRequest, domain_id: int, level: int):
#     return get_object_or_404(
#         SelectedMaturityMatrixAssessment, maturitymatrix__id=domain_id, assessment__level=level
#     )
