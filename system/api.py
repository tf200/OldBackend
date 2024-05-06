from typing import Any
from uuid import UUID

from django.db.models import ExpressionWrapper, F, FloatField, Sum
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from easyaudit.models import CRUDEvent
from loguru import logger
from ninja import Query, Router, UploadedFile
from ninja.pagination import paginate

from adminmodif.models import Group, Permission
from authentication.models import Location
from client.models import ClientDetails, Contract, Invoice
from employees.models import (
    ClientMedication,
    ClientMedicationRecord,
    EmployeeProfile,
    GroupAccess,
)
from system.filters import ExpenseSchemaFilter
from system.models import AttachmentFile, DBSettings, Expense, Notification
from system.schemas import (
    ActivityLogSchema,
    AttachmentFilePatch,
    AttachmentFileSchema,
    DBSettingsSchema,
    EmptyResponseSchema,
    ErrorResponseSchema,
    ExpenseSchema,
    ExpenseSchemaInput,
    ExpenseSchemaPatch,
    GroupAccessDelete,
    GroupAccessInput,
    GroupAccessSchema,
    GroupSchema,
    GroupSchemaInput,
    GroupSchemaPatch,
    GroupsListSchema,
    NotificationSchema,
)
from system.utils import NinjaCustomPagination

router = Router()


@router.get("/settings", response=DBSettingsSchema)
def settings(request: HttpRequest):
    return DBSettingsSchema()


@router.get("/notifications", response=list[NotificationSchema])
@paginate(NinjaCustomPagination)
def notifications(request: HttpRequest):
    user = request.user
    return Notification.objects.filter(receiver=user).all()


@router.post(
    "/notifications/{id}/read",
    response={
        201: EmptyResponseSchema,
        404: ErrorResponseSchema,
        401: ErrorResponseSchema,
    },
)
def mark_as_read(request, id: int):
    try:
        notification = Notification.objects.get(id=id)

        if notification.receiver == request.user:
            notification.is_read = True
            notification.save()
            return 201, {}
        return 401, {"message", "Unauthorized action/request!"}
    except Notification.DoesNotExist:
        return 404, {"message": "Notification not found"}


@router.get("/attachments", response=list[AttachmentFileSchema])
@paginate(NinjaCustomPagination)
def attachments(request: HttpRequest):
    return AttachmentFile.objects.all()


@router.post("/attachments/upload", response=AttachmentFileSchema)
def upload_attachment(request: HttpRequest, file: UploadedFile):
    return AttachmentFile.objects.create(name=file.name, file=file, size=file.size)


@router.get("/attachments/{uuid}", response=AttachmentFileSchema)
def attachment_details(request: HttpRequest, uuid: UUID):
    return get_object_or_404(AttachmentFile, id=uuid)


@router.delete(
    "/attachments/{uuid}/delete", response={204: EmptyResponseSchema, 500: ErrorResponseSchema}
)
def delete_attachment(request: HttpRequest, uuid: UUID):
    try:
        AttachmentFile.objects.filter(id=uuid).delete()
        return 204, {}
    except Exception:
        logger.exception()  # type: ignore
    return 500, "Oops! something went wrong, please try again or later."


@router.patch("/attachments/{uuid}/update", response=AttachmentFileSchema)
def update_attachment(request: HttpRequest, uuid: UUID, attachment: AttachmentFilePatch):
    AttachmentFile.objects.filter(id=uuid).update(**attachment.dict(exclude_unset=True))
    return get_object_or_404(AttachmentFile, id=uuid)


@router.get("/expenses", response=list[ExpenseSchema])
@paginate(NinjaCustomPagination)
def expenses(request: HttpRequest, filter: ExpenseSchemaFilter = Query()):  # type: ignore
    return filter.filter(Expense.objects.all())


@router.post("/expenses/add", response=ExpenseSchema)
def add_expense(request: HttpRequest, expense: ExpenseSchemaInput):
    return Expense.objects.create(**expense.dict())


@router.patch("/expenses/{int:expense_id}/update", response=ExpenseSchema)
def patch_expense(request: HttpRequest, expense_id: int, expense: ExpenseSchemaPatch):
    Expense.objects.filter(id=expense_id).update(**expense.dict(exclude_unset=True))
    return get_object_or_404(Expense, id=expense_id)


@router.delete("/expenses/{int:expense_id}/delete", response={204: EmptyResponseSchema})
def delete_expense(request: HttpRequest, expense_id: int):
    Expense.objects.filter(id=expense_id).delete()
    return 204, {}


@router.get("/dashboard/analytics", tags=["analytics"])
def dashboard(request: HttpRequest):
    """
    Ensure to return all the needed info:
    - Users (Total users, number In care, out of care, on waiting list users)
    - Contracts (Total contracts, number of approved contracts, number of terminated contracts)
    - medications (total medications, number of critical medications, number of medication records, number of taken/not taken medications)
    - Invoices (Total invoices, number of paid invoices, number of unpaid invoices)
    - Reports (Total number of reports)
    - Revenue (Total income, total outcome/cost)
    """

    # Fetch all the needed data from DB here, then pass it to the dectionary bellow

    return {
        # User's stats
        "users": {
            "total_users": ClientDetails.objects.count(),
            "total_in_care_users": ClientDetails.objects.filter(status="In Care").count(),
            "total_out_of_care_users": ClientDetails.objects.filter(status="Out Of Care").count(),
            "total_on_waiting_list_users": ClientDetails.objects.filter(
                status="On Waiting List"
            ).count(),
        },
        # Contract stats
        "contracts": {
            "total_contracts": Contract.objects.count(),
            "total_accommodation_contracts": Contract.objects.filter(
                care_type=Contract.CareTypes.ACCOMMODATION
            ).count(),
            "total_ambulante_contracts": Contract.objects.filter(
                care_type=Contract.CareTypes.AMBULANTE
            ).count(),
            "total_approved_contracts": Contract.objects.filter(
                status=Contract.Status.APPROVED
            ).count(),
            "total_stopped_contracts": Contract.objects.filter(
                status=Contract.Status.STOPPED
            ).count(),
            "total_terminated_contracts": Contract.objects.filter(
                status=Contract.Status.TERMINATED
            ).count(),
        },
        # Medication's stats
        "medications": {
            "total_attachments": AttachmentFile.objects.filter(is_used=True).count(),
            "total_medications": ClientMedication.objects.count(),
            "total_critical_medications": ClientMedication.objects.filter(
                is_critical=True
            ).count(),
            "total_medication_records": ClientMedicationRecord.objects.count(),
            "total_taken_medication_records": ClientMedicationRecord.objects.filter(
                status=ClientMedicationRecord.Status.TAKEN
            ).count(),
            "total_not_taken_medication_records": ClientMedicationRecord.objects.filter(
                status=ClientMedicationRecord.Status.NOT_TAKEN
            ).count(),
            "total_waiting_medication_records": ClientMedicationRecord.objects.filter(
                status=ClientMedicationRecord.Status.AWAITING
            ).count(),
        },
        # Financial stats
        ## Invoice's stats
        "invoices": {
            "total_invoices": Invoice.objects.count(),
            "total_paid_invoices": Invoice.objects.filter(status=Invoice.Status.PAID).count(),
            "total_partially_paid_invoices": Invoice.objects.filter(
                status=Invoice.Status.PARTIALLY_PAID
            ).count(),
            "total_outstanding_invoices": Invoice.objects.filter(
                status=Invoice.Status.OUTSTANDING
            ).count(),
            "total_overpaid_invoices": Invoice.objects.filter(
                status=Invoice.Status.OVERPAID
            ).count(),
        },
        ### Total income
        "finance": {
            "total_paid_amount": Invoice.objects.values_list(
                "history__amount", flat=True
            ).aggregate(total=Sum("history__amount"))["total"],
            # ## Fetch the costs/charges (outcome)
            "total_expenses": Expense.objects.aggregate(
                total=Sum(
                    ExpressionWrapper(
                        F("amount") * (1 + F("tax") / 100), output_field=FloatField()
                    )
                )
            )["total"],
        },
    }


@router.get("/dashboard/analytics/locations", response=list[dict[str, Any]], tags=["analytics"])
def locations_stats(request: HttpRequest):
    locations = Location.objects.all()

    location_stats = []

    for location in locations:
        location_stats.append(
            {
                "location_name": location.name,
                "location_id": location.id,
                "location_capacity": location.capacity,
                "total_employees": location.employee_location.count(),
                "total_clients": location.client_location.filter(
                    contracts__care_type=Contract.CareTypes.ACCOMMODATION
                ).count(),
                "total_expenses": location.get_total_expenses(),
                "total_revenue": location.get_total_revenue(),
            }
        )

    return location_stats


# @router.get("/dashboard/analytics/expenses")
# def expense_graphs(request: HttpRequest):
#     Expense.objects.cr


# Activity Log
@router.get("/logs/activities", response=list[ActivityLogSchema])
@paginate(NinjaCustomPagination)
def activity_logs(request: HttpRequest):
    return CRUDEvent.objects.all()


# Permissions


@router.get("/administration/permissions", tags=["permissions"])
def all_permissions(request: HttpRequest):
    return [perm.name for perm in Permission.objects.all()]


@router.get("/administration/groups", response=list[GroupSchema], tags=["permissions"])
def all_groups(request: HttpRequest):
    return Group.objects.all()


@router.get("/administration/permissions/{int:employee_id}", tags=["permissions"])
def employee_permissions(request: HttpRequest, employee_id: int):
    employee = get_object_or_404(EmployeeProfile, id=employee_id)
    return [perm.name for perm in employee.get_permissions()]


@router.get(
    "/administration/groups/employee/{int:employee_id}",
    response=list[GroupSchema],
    tags=["permissions"],
)
def employee_groups(request: HttpRequest, employee_id: int):
    employee = get_object_or_404(EmployeeProfile, id=employee_id)
    return employee.groups.all()


@router.get("/administration/groups/{int:group_id}", response=GroupSchema, tags=["permissions"])
def group_details(request: HttpRequest, group_id: int):
    return get_object_or_404(Group, id=group_id)


@router.post("/administration/groups/add", response=GroupSchema, tags=["permissions"])
def add_group(request: HttpRequest, group: GroupSchemaInput):
    permissions: list[str] = group.permissions
    new_group = Group.objects.create(name=group.name)
    for perm in Permission.objects.filter(name__in=permissions).all():
        new_group.permissions.add(perm)
    return new_group


@router.patch(
    "/administration/groups/{int:group_id}/update", response=GroupSchema, tags=["permissions"]
)
def patch_group(request: HttpRequest, group_id: int, paylaod: GroupSchemaPatch):
    group = get_object_or_404(Group, id=group_id)

    # Update name
    if paylaod.name:
        group.name = paylaod.name
        group.save()

    # Delete all permissions
    group.permissions.clear()

    for perm in Permission.objects.filter(name__in=paylaod.permissions).all():
        group.permissions.add(perm)
    return group


@router.delete(
    "/administration/groups/{int:group_id}/delete",
    response={204: EmptyResponseSchema},
    tags=["permissions"],
)
def delete_group(request: HttpRequest, group_id: int):
    Group.objects.filter(id=group_id).delete()
    return 204, {}


# @router.post(
#     "/administration/groups/assign/{int:employee_id}",
#     response={204: EmptyResponseSchema},
#     tags=["permissions"],
# )
# def assign_group_to_employee(request: HttpRequest, employee_id: int, payload: GroupsListSchema):
#     employee = get_object_or_404(EmployeeProfile, id=employee_id)
#     # Remove old groups
#     employee.groups.clear()

#     for group in Group.objects.filter(id__in=payload.groups).all():
#         employee.groups.add(group)

#     return 204, {}


@router.post(
    "/administration/group-access/assign-group", response=GroupAccessSchema, tags=["permissions"]
)
def add_group_access_to_an_employee(request: HttpRequest, group: GroupAccessInput):
    return GroupAccess.objects.create(**group.dict())


@router.get(
    "/administration/group-access/employee/{int:employee_id}",
    response=list[GroupAccessSchema],
    tags=["permissions"],
)
def employee_group_access(request: HttpRequest, employee_id: int):
    employee = get_object_or_404(EmployeeProfile, id=employee_id)
    return GroupAccess.objects.filter(employee=employee).all()


@router.delete(
    "/administration/group-access/{int:group_access_id}/delete",
    response={204: EmptyResponseSchema},
    tags=["permissions"],
)
def delete_employee_group_access_by_id(request: HttpRequest, group_access_id: int):
    # employee = get_object_or_404(EmployeeProfile, id=employee_id)
    GroupAccess.objects.filter(id=group_access_id).delete()
    return 204, {}


@router.delete(
    "/administration/group-access/employee/{int:employee_id}/group/{int:group_id}/delete",
    response={204: EmptyResponseSchema},
    tags=["permissions"],
)
def delete_employee_group_access(request: HttpRequest, employee_id: int, group_id: int):
    GroupAccess.objects.filter(employee__id=employee_id, group__id=group_id).delete()
    return 204, {}
