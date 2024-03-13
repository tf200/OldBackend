from django_filters.rest_framework import DjangoFilterBackend
from django.template.loader import render_to_string
from weasyprint import HTML
from rest_framework.permissions import IsAuthenticated
from adminmodif.permissions import IsMemberOfAuthorizedGroup
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from .tasks import send_progress_report_email
from .pagination import CustomPagination
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import generics
from employees.models import ClientMedication
from django.shortcuts import render
from .models import ClientDetails 
from rest_framework.views import APIView
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from adminmodif.models import Group
from employees.utils import generate_unique_username
from django.contrib.auth.hashers import make_password
from client.filters import *
from .serializers import *
from rest_framework import filters , status
from authentication.models import CustomUser
from adminmodif.models import GroupMembership
# Create your views here.


class ClientCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            client_data = request.data
            first_name = client_data.get('first_name', '')
            last_name = client_data.get('last_name', '')
            username = generate_unique_username(first_name, last_name)
            password = make_password(None)
            user, user_created = CustomUser.objects.get_or_create(username=username)
            if user_created:
                user.set_password(password)
                user.save()
                client_group, group_created = Group.objects.get_or_create(name='Client')

                # Create a new GroupMembership for the user, linking them to the 'Client' group
                # Since you want the membership to be permanent and effective immediately,
                # you leave the start_date and end_date as None
                GroupMembership.objects.create(
                    user=user,
                    group=client_group,
                    start_date=None,  # Immediate effect
                    end_date=None     # Permanence
    )
            else:
                if hasattr(user, 'profile'):
                    return Response({"error": "This user already has an associated EmployeeProfile."},
                                    status=status.HTTP_400_BAD_REQUEST)
            try:
                client_profile = ClientDetails.objects.create(user=user, **client_data)
                serializer = ClientDetailsSerializer(client_profile)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)            






class ClientDetailsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientDetailsSerializer
    queryset = ClientDetails.objects.all()


class ClientListView (generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientDetailsSerializer
    queryset = ClientDetails.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {'status': ['exact', 'in']}
    search_fields = ['first_name', 'last_name', 'status', 'date_of_birth', 'identity', 'email', 'phone_number', 'organisation',
                     'location', 'departement', 'gender', 'filenumber', 'city', 'Zipcode', 'infix', 'streetname', 'street_number']
    # filterset_class = ClientDetailsFilter
    ordering_fields = ['first_name', 'last_name',
                       'date_of_birth', 'city', 'streetname']
    ordering = ['-created']
    pagination_class = CustomPagination


class ClientUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientDetailsSerializer
    queryset = ClientDetails.objects.all()


class ClientDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientDetailsSerializer
    queryset = ClientDetails.objects.all()

# ====================================================


class DiagnosisCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientDiagnosisSerializer


class DiagnosisRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientDiagnosisSerializer
    queryset = ClientDiagnosis.objects.all()


class DiagnosisListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientDiagnosisSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ClientDiagnosisFilter
    ordering_fields = ['title', 'date_of_diagnosis',
                       'severity', 'status', 'diagnosing_clinician']
    ordering = ['-created']
    pagination_class = CustomPagination  # Use your custom pagination class

    def get_queryset(self):
        client_id = self.kwargs['client']
        return ClientDiagnosis.objects.filter(client=client_id)


class DiagnosisUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientDiagnosisSerializer
    queryset = ClientDiagnosis.objects.all()


class DiagnosisDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientDiagnosisSerializer
    queryset = ClientDiagnosis.objects.all()

# =======================================================================


class ClientEmergencyContactCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientEmergencyContactSerializer


class ClientEmergencyContactRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientEmergencyContactSerializer
    queryset = ClientEmergencyContact.objects.all()


class ClientEmergencyContactListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientEmergencyContactSerializer
    ordering = ['-created']
    pagination_class = CustomPagination

    def get_queryset(self):
        client_id = self.kwargs['client']
        return ClientEmergencyContact.objects.filter(client=client_id)


class ClientEmergencyContactUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientEmergencyContactSerializer
    queryset = ClientEmergencyContact.objects.all()


class ClientEmergencyContactDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientEmergencyContactSerializer
    queryset = ClientEmergencyContact.objects.all()


# ==========================================================================


class ClientDocumentsUploadView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientDocumentsSerializers


class ClientDocumentsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientDocumentsSerializers
    ordering = ['-created']
    pagination_class = CustomPagination

    def get_queryset(self):
        client_id = self.kwargs['client']
        return ClientDocuments.objects.filter(user=client_id)


class ClientDocumentsDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientDocumentsSerializers
    queryset = ClientDocuments.objects.all()


# ========================================================================


class ClientMedicationCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientMedicationSerializer


class ClientMedicationRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientMedicationSerializer
    queryset = ClientMedication.objects.all()


class ClientMedicationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientMedicationSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ClientMedicationFilter
    ordering_fields = ['name', 'dosage', 'frequency', 'start_date', 'end_date']
    ordering = ['-created']

    def get_queryset(self):
        client_id = self.kwargs['client']
        return ClientMedication.objects.filter(client=client_id)


class ClientMedicationUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientMedicationSerializer
    queryset = ClientMedication.objects.all()


class ClientMedicationDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientMedicationSerializer
    queryset = ClientMedication.objects.all()


# ================================================================

class ClientAllergyCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientAllergySerializer


class ClientAllergyRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientAllergySerializer
    queryset = ClientAllergy.objects.all()


class ClientAllergyListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientAllergySerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ClientAllergyFilter
    ordering_fields = ['allergy_type', 'severity', 'reaction']
    ordering = ['-created']

    def get_queryset(self):
        client_id = self.kwargs['client']
        return ClientAllergy.objects.filter(client=client_id)


class ClientAllergyUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientAllergySerializer
    queryset = ClientAllergy.objects.all()


class ClientAllergyDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ClientAllergySerializer
    queryset = ClientAllergy.objects.all()

# =================================================================================


# class ProgressReportCreateView(generics.CreateAPIView):
#     permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
#     serializer_class = ClientprogressSerializer
#     def perform_create(self, serializer):
#         instance = serializer.save()  # Save the instance created by the serializer
#         send_progress_report_email.delay(instance.id , instance.report_text)

# class ProgressReportRetrieveView(generics.RetrieveAPIView):
#     permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
#     serializer_class = ClientprogressSerializer
#     queryset = ProgressReport.objects.all()

# class ProgressReportListView(generics.ListAPIView):
#     permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
#     serializer_class = ClientprogressSerializer
#     filter_backends = [DjangoFilterBackend, OrderingFilter]
#     # filterset_class = ProgressReportFilter  # Uncomment this if you have a filter class
#     ordering_fields = ['date', 'client']
#     ordering = ['date']
#     pagination_class = CustomPagination  # Use your custom pagination class

#     def get_queryset(self):
#         client_id = self.kwargs['client']
#         return ProgressReport.objects.filter(client=client_id)

# class ProgressReportUpdateView(generics.UpdateAPIView):
#     permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
#     serializer_class = ClientprogressSerializer
#     queryset = ProgressReport.objects.all()

# class ProgressReportDeleteView(generics.DestroyAPIView):
#     permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
#     serializer_class = ClientprogressSerializer
#     queryset = ProgressReport.objects.all()


# =============================================================
class ContractCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ContractSerializer


class ContractRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ContractSerializer
    queryset = Contract.objects.all()


class ContractListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ContractSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    # filterset_class = ContractFilter
    ordering_fields = ['start_date', 'end_date',
                       'rate_per_day', 'rate_per_minute', 'rate_per_hour']
    ordering = ['-created']

    def get_queryset(self):
        client_id = self.kwargs.get('client', None)
        if client_id is not None:
            return Contract.objects.filter(client=client_id)
        return Contract.objects.all()


class ContractUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ContractSerializer
    queryset = Contract.objects.all()


class ContractDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ContractSerializer
    queryset = Contract.objects.all()


# ======================================================



class ClientTypeCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ClientTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientTypeListView(generics.ListAPIView):
    queryset = ClientType.objects.all()
    serializer_class = ClientTypeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'address', 'phone_number']



class SenderRetrieveAPIView(APIView):
    def get(self, request, client_id):
        try:
            # Retrieve the client by ID
            client = ClientDetails.objects.get(pk=client_id)
            # Use the sender associated with the client
            sender = client.sender
            # Serialize the sender data
            serializer = ClientTypeSerializer(sender)
            return Response(serializer.data)
        except ClientDetails.DoesNotExist:
            return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
        




class TemporaryFileUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TemporaryFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Return the ID of the temporary file for later reference
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class GenerateInvoiceAPI(APIView):
    def post(self, request, *args, **kwargs):
        contract_id = request.data.get('contract_id')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        contract = get_object_or_404(Contract, id=contract_id)
        cost = contract.calculate_cost_for_period(start_date, end_date)

        invoice = Invoice.objects.create(
            client=contract,
            due_date=end_date,
            pre_vat_total=cost,
        )

        invoice.calculate_totals()

        # Generate PDF
        context = self.get_context_data(invoice, contract)
        html_string = render_to_string('invoice_template.html', context)
        html = HTML(string=html_string)
        pdf_content = html.write_pdf()
        invoice_filename = f'invoice_{invoice.invoice_number}.pdf'

        # Save the PDF content
        if default_storage.exists(invoice_filename):
            default_storage.delete(invoice_filename)
        default_storage.save(invoice_filename, ContentFile(pdf_content))

        # Update the Invoice instance with the PDF URL
        invoice_pdf_url = default_storage.url(invoice_filename)
        invoice.url = invoice_pdf_url
        invoice.save(update_fields=['url'])

        # Serialize and return the updated invoice
        invoice_serializer = InvoiceSerializer(invoice)
        response_data = invoice_serializer.data
        response_data['pdf_url'] = invoice_pdf_url  # Ensure the response includes the PDF URL

        return Response(response_data, status=status.HTTP_201_CREATED)

    def get_context_data(self, invoice, contract):
        """Prepare context data for rendering the invoice PDF."""
        client_type = contract.sender
        return {
            'company_name': client_type.name,
            'email': client_type.email_adress,
            'address': client_type.address,
            'client': f'{contract.client.first_name} {contract.client.last_name}',
            'vat_rate': invoice.vat_rate,
            'vat_amount': invoice.vat_amount,
            'total_amount': invoice.total_amount,
            'pre_vat_total': invoice.pre_vat_total,
            'issue_date': invoice.issue_date,
            'invoice_number': invoice.invoice_number,
            # Add other necessary fields as needed
        }
    


class InvoiceListView(generics.ListAPIView):
    serializer_class = InvoiceSerializer

    def get_queryset(self):

        client_id = self.kwargs['client_id']     
        client = get_object_or_404(Contract, id=client_id)  # Ensures the client exists
        return Invoice.objects.filter(client=client).order_by('-issue_date')
