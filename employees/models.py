from __future__ import annotations

import uuid
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from loguru import logger

from adminmodif.models import Group, Permission
from assessments.models import AssessmentDomain
from authentication.models import Location
from client.models import ClientDetails
from system.models import Notification


class EmployeeProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    position = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    employee_number = models.CharField(max_length=50, null=True, blank=True)
    employment_number = models.CharField(max_length=50, null=True, blank=True)
    private_email_address = models.EmailField(null=True, blank=True)
    email_address = models.EmailField(null=True, blank=True)
    # Education
    authentication_phone_number = models.CharField(max_length=100, null=True, blank=True)
    private_phone_number = models.CharField(max_length=100, null=True, blank=True)
    work_phone_number = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    home_telephone_number = models.CharField(max_length=100, null=True, blank=True)

    groups = models.ManyToManyField(Group, through="GroupAccess")

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    is_subcontractor = models.BooleanField(null=True, blank=True)
    gender = models.CharField(max_length=100, null=True, blank=True)
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, related_name="employee_location"
    )
    has_borrowed = models.BooleanField(default=False)

    out_of_service = models.BooleanField(default=False, null=True, blank=True)
    is_archived = models.BooleanField(default=False, null=True, blank=True)

    class Meta:
        ordering = ("-id",)

    def __str__(self) -> str:
        return f"Employee: {self.first_name} ({self.pk})"

    def __repr__(self) -> str:
        return f"Employee: {self.first_name} ({self.pk})"

    def get_permissions(self) -> QuerySet[Permission]:
        return Permission.objects.filter(id__in=self.get_permission_ids())

    def get_permission_ids(self) -> list[int]:
        today = timezone.now()
        return list(
            filter(
                lambda a: a,
                EmployeeProfile.objects.filter(id=self.pk)
                .filter(
                    Q(groups__groupaccess__start_date__lte=today)
                    | Q(groups__groupaccess__start_date__isnull=True),
                    Q(groups__groupaccess__end_date__gte=today)
                    | Q(groups__groupaccess__end_date__isnull=True),
                )
                .values_list("groups__permissions", flat=True),
            )
        )

    def has_permission(self, permission_name: str) -> bool:
        return self.__class__.objects.filter(groups__permissions__name=permission_name).exists()


# this is a Group Access
class Certification(models.Model):
    employee = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE, related_name="certifications"
    )
    name = models.CharField(max_length=255)
    issued_by = models.CharField(max_length=255)
    date_issued = models.DateField()
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.name


class Experience(models.Model):
    employee = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE, related_name="experiences"
    )
    job_title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)


class Education(models.Model):
    employee = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE, related_name="education_history"
    )
    institution_name = models.CharField(max_length=255)
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.degree} in {self.field_of_study} from {self.institution_name}"


class Assignment(models.Model):
    employee = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE, related_name="assignments"
    )
    client = models.ForeignKey(
        ClientDetails, on_delete=models.CASCADE, related_name="assigned_employees"
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(
        max_length=50,
        choices=[
            ("Confirmed", "Confirmed"),
            ("Pending", "Pending"),
            ("Cancelled", "Cancelled"),
        ],
    )
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.employee} assigned to {self.client} from {self.start_datetime} to {self.end_datetime}"

    def clean(self):

        overlapping_assignments = Assignment.objects.filter(
            employee=self.employee,
            start_datetime__lt=self.end_datetime,
            end_datetime__gt=self.start_datetime,
        )
        if overlapping_assignments.exists():
            raise ValidationError("This assignment overlaps with another.")

        # Check if the employee is available
        if not self.employee.availabilities.filter(
            start_datetime__lte=self.start_datetime, end_datetime__gte=self.end_datetime
        ).exists():
            raise ValidationError("The employee is not available at this time.")

        # Check if employee's skills match client's requirements
        if not self.employee.skills.filter(id__in=self.client.required_skills.all()).exists():
            raise ValidationError(
                "The employee does not have the required skills for this client."
            )


class ClientEmployeeAssignment(models.Model):
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE)
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    start_date = models.DateField()
    role = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)


class ProgressReport(models.Model):
    class Types(models.TextChoices):
        MORNING_REPORT = (
            "morning_report",
            "Morning report",
        )
        EVENING_REPORT = (
            "evening_report",
            "Evening report",
        )
        NIGHT_REPORT = (
            "night_report",
            "Night report",
        )
        SHIFT_REPORT = (
            "shift_report",
            "Intermediate shift report",
        )
        ONE_TO_ONE_REPORT = (
            "one_to_one_report",
            "1 on 1 Reporting",
        )
        PROCESS_REPORT = (
            "process_report",
            "Process Reporting",
        )
        CONTACT_JOURNAL = "contact_journal", "Contact Journal"
        OTHER = "other", "Other"

    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    report_text = models.TextField()
    author = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name="author",
        blank=True,
        null=True,
    )

    type = models.CharField(choices=Types.choices, default=Types.OTHER)

    created = models.DateTimeField(blank=True, null=True)


class Measurement(models.Model):
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    measurement_type = models.CharField(max_length=100)
    value = models.FloatField()
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)


class Observations(models.Model):
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE)
    category = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    observation_text = models.TextField()
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)


class Feedback(models.Model):
    author = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name="author1",
        blank=True,
        null=True,
    )
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    feedback_text = models.TextField()
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)


class EmotionalState(models.Model):
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE)
    date = models.DateTimeField()
    state_description = models.TextField()
    intensity = models.IntegerField()  # You can use a scale like 1-10
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Emotional State for {self.client.name} - {self.date}"


class PhysicalState(models.Model):
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE)
    date = models.DateTimeField()
    symptoms = models.TextField()
    severity = models.IntegerField()  # You can use a scale like 1-10
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Physical State for {self.client.name} - {self.date}"


class ClientMedication(models.Model):
    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    self_administered = models.BooleanField(default=True)

    slots = models.JSONField(default=list, blank=True, null=True)

    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE, related_name="medications")
    administered_by = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name="medications_administered",
    )

    is_critical = models.BooleanField(default=False)

    updated = models.DateTimeField(auto_now=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True, db_index=True)

    class Meta:
        ordering = ("-created",)

    def get_days(self) -> list[datetime]:
        """Returns a list of days which medications will be taken"""
        # [
        #     {
        #         date: "2024-05-10",
        #         times: ["12:33", "15:66", "48:54"]
        #     },
        # ]
        days = [slot["date"] for slot in self.slots]
        return [datetime.fromisoformat(day.split(".")[0]) for day in days]

    def get_available_slots(self) -> list[datetime]:
        """Returns a list stots (datetime) when a medicen should be taken"""
        # [
        #     {
        #         date: "2024-05-10",
        #         times: ["12:33", "15:66", "48:54"]
        #     },
        # ]
        available_datetime: list[datetime] = []

        for slot in self.slots:
            day = datetime.fromisoformat(slot["date"].split(".")[0])
            for time in slot["times"]:
                hours, minutes = [int(value) for value in time.split(":")]
                available_datetime.append(day.replace(hour=hours, minute=minutes))

        return available_datetime

    def create_medication_records(self) -> None:
        for slot in self.get_available_slots():
            ClientMedicationRecord.objects.create(
                client_medication=self,
                time=slot,
            )


class ClientMedicationRecord(models.Model):
    class Status(models.TextChoices):
        TAKEN = "taken", "Taken"
        NOT_TAKEN = "not_taken", "Not Taken"
        AWAITING = "awaiting", "Awaiting"

    client_medication = models.ForeignKey(
        ClientMedication, related_name="records", on_delete=models.CASCADE
    )
    status = models.CharField(
        choices=Status.choices, default=Status.AWAITING, null=True, blank=True
    )
    reason = models.TextField(default="", null=True, blank=True)
    time = models.DateTimeField(db_index=True)

    updated = models.DateTimeField(auto_now=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created",)

    def notify(self):
        logger.debug(f"Send Medical Notification {self.id}")
        # inform client as well as his employee
        # Send to the client
        notification = Notification.objects.create(
            title=f"It's time to take your medication (#{self.id}).",
            event=Notification.EVENTS.MEDICATION_TIME,
            content=f"You have a medication to take.",
            receiver=self.client_medication.client.user,
            metadata={"medication_id": self.client_medication.id, "medication_record_id": self.id},
        )

        notification.notify()

        # Send to the employee
        notification = Notification.objects.create(
            title=f"Medication record (#{self.id}).",
            event=Notification.EVENTS.MEDICATION_TIME,
            content=f"You have a medication record to fill up.",
            receiver=self.client_medication.administered_by.user,
            metadata={"medication_id": self.client_medication.id, "medication_record_id": self.id},
        )

        notification.notify()


class ClientGoals(models.Model):
    client = models.ForeignKey(
        ClientDetails, on_delete=models.CASCADE, related_name="client_goals"
    )
    goal_name = models.CharField(max_length=100)
    goal_details = models.CharField(max_length=500)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    administered_by = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="emp_goals",
    )


class GoalsReport(models.Model):
    goal = models.ForeignKey(
        ClientGoals, on_delete=models.SET_NULL, related_name="goals_report", null=True
    )
    title = models.CharField(max_length=100)
    report_text = models.TextField()
    rating = models.IntegerField(null=True, blank=True)
    created_at_sys = models.DateTimeField(auto_now_add=True, null=True)
    created_at = models.DateTimeField(null=True)


class AiGeneratedWeeklyReports(models.Model):
    report_text = models.TextField()
    goal = models.ForeignKey(ClientGoals, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class WeeklyReportSummary(models.Model):
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE)
    summary_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Incident(models.Model):
    # Assuming 'Employee' and 'Child' models are defined elsewhere
    reported_by = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE, related_name="reported_incidents"
    )
    involved_children = models.ManyToManyField(ClientDetails, related_name="incidents")
    date_reported = models.DateTimeField(default=timezone.now)
    date_of_incident = models.DateTimeField()
    location = models.CharField(max_length=255)
    description = models.TextField()
    action_taken = models.TextField(blank=True, null=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=100,
        default="Reported",
        choices=(
            ("Reported", "Reported"),
            ("Under Investigation", "Under Investigation"),
            ("Resolved", "Resolved"),
            ("Closed", "Closed"),
        ),
    )

    class Meta:
        verbose_name = "Incident"
        verbose_name_plural = "Incidents"

    def __str__(self):
        return f"Incident on {self.date_of_incident} at {self.location}"


class DomainGoal(models.Model):
    title = models.CharField(max_length=255)
    desc = models.TextField(default="", null=True, blank=True)

    domain = models.ForeignKey(
        AssessmentDomain, related_name="goals", on_delete=models.SET_NULL, null=True
    )
    client = models.ForeignKey(ClientDetails, related_name="goals", on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        EmployeeProfile,
        related_name="goals",
        on_delete=models.SET_NULL,
        null=True,
    )
    reviewed_by = models.ForeignKey(
        EmployeeProfile,
        related_name="reviewed_goals",
        on_delete=models.SET_NULL,
        null=True,
    )
    is_approved = models.BooleanField(default=False)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self) -> str:
        return f"Main Goal: {self.title}"

    def total_objectives(self) -> int:
        return self.objectives.count()

    def main_goal_rating(self) -> float:
        """This average is calculated based on Objectives"""
        objectives = self.objectives.all()
        if objectives:
            return round(sum([objective.rating for objective in objectives]) / len(objectives), 1)
        return 0

    def save(self, *args, **kwargs):
        # if not self.id:
        #     # creating
        #     self.created_by = self.request.user
        # else:
        #     # updating
        #     old_goal = get_object_or_404(self.__class__, id=self.id)
        #     if old_goal.is_approved != self.is_approved:
        #         self.reviewed_by = self.request.user

        return super(self.__class__, self).save(*args, **kwargs)


class DomainObjective(models.Model):
    title = models.CharField(max_length=255)
    desc = models.TextField(default="", null=True, blank=True)
    rating = models.FloatField(default=0)

    goal = models.ForeignKey(
        DomainGoal, related_name="objectives", on_delete=models.SET_NULL, null=True
    )
    client = models.ForeignKey(ClientDetails, related_name="objectives", on_delete=models.CASCADE)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Objective: {self.title}"


class ObjectiveHistory(models.Model):
    rating = models.FloatField(default=0)
    week = models.IntegerField(db_index=True)
    date = models.DateField(auto_now_add=True, db_index=True)
    objective = models.ForeignKey(
        DomainObjective, related_name="history", on_delete=models.CASCADE
    )
    content = models.TextField(default="", null=True, blank=True)

    class Meta:
        unique_together = ["week", "objective"]
        ordering = ("week",)

    def save(self, *args, **kwargs):
        if not self.pk:
            # create
            # Let's update the objective rating
            objective = self.objective
            objective.rating = self.rating
            objective.save()
        else:
            # Updating
            # get the latest report/evaluation
            latest_objective_history = self.__class__.objects.first()  # Get the latest evaluation
            if latest_objective_history.id == self.id:
                objective = self.objective
                objective.rating = self.rating  # the new rating
                objective.save()

        result = super().save(*args, **kwargs)
        return result


class GoalHistory(models.Model):
    rating = models.FloatField(default=0)
    date = models.DateField(auto_now_add=True, db_index=True)
    goal = models.ForeignKey(DomainGoal, related_name="history", on_delete=models.CASCADE)


class GroupAccess(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self) -> str:
        return f'GroupAccess: "{self.group.name} ({self.pk})"'

    def __repr__(self) -> str:
        return f'GroupAccess: "{self.group.name} ({self.pk})"'
