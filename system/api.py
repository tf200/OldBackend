from uuid import UUID

from django.db.models import Sum
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from loguru import logger
from ninja import Router, UploadedFile
from ninja.pagination import paginate

from client.models import ClientDetails, Contract, Invoice
from employees.models import ClientMedication, ClientMedicationRecord
from system.models import AttachmentFile, DBSettings, Expense, Notification
from system.schemas import (
    AttachmentFilePatch,
    AttachmentFileSchema,
    DBSettingsSchema,
    EmptyResponseSchema,
    ErrorResponseSchema,
    ExpenseSchema,
    ExpenseSchemaInput,
    ExpenseSchemaPatch,
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
def expenses(request: HttpRequest):
    return Expense.objects.all()


@router.post("/expenses/add", response=ExpenseSchema)
def add_expense(request: HttpRequest, expense: ExpenseSchemaInput):
    return Expense.objects.create(**expense.dict())


@router.patch("/expenses/{int:expense_id}", response=ExpenseSchema)
def patch_expense(request: HttpRequest, expense_id: int, expense: ExpenseSchemaPatch):
    Expense.objects.filter(id=expense_id).update(**expense.dict(exclude_unset=True))
    return get_object_or_404(Expense, id=expense_id)


@router.delete("/expenses/{int:expense_id}/delete", response={204: EmptyResponseSchema})
def delete_expense(request: HttpRequest, expense_id: int):
    Expense.objects.filter(id=expense_id).delete()
    return 204, {}


@router.get("/dashboard/analytics")
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
            "total_paid_amount": round(
                sum([invoice.total_paid_amount() for invoice in Invoice.objects.all()]), 2
            ),
            ## Fetch the costs/charges (outcome)
            "total_expenses": Expense.objects.aggregate(total=Sum("amount"))["total"],
        },
    }
