from django_filters.rest_framework import DjangoFilterBackend
from django.template.loader import render_to_string
from weasyprint import HTML
from rest_framework.permissions import IsAuthenticated
from adminmodif.permissions import IsMemberOfAuthorizedGroup , IsMemberOfManagement
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
from django.db.models import Sum

# Create your views here.


class ClientCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            client_data = request.data
            first_name = client_data.get('first_name', '')
            last_name = client_data.get('last_name', '')
            # Assuming generate_unique_username is a utility function you've defined
            username = generate_unique_username(first_name, last_name)
            password = make_password(None)
            user, user_created = CustomUser.objects.get_or_create(username=username)
            if user_created:
                user.set_password(password)
                user.save()
                client_group, group_created = Group.objects.get_or_create(name='Client')
                # Assuming GroupMembership is a model you've defined for group membership
                GroupMembership.objects.create(
                    user=user,
                    group=client_group,
                    start_date=None,
                    end_date=None
                )
            else:
                if hasattr(user, 'profile'):
                    return Response({"error": "This user already has an associated EmployeeProfile."},
                                    status=status.HTTP_400_BAD_REQUEST)
            
            # Fetch the Location instance using the ID provided in client_data
            location_id = client_data.get('location')
            if location_id is not None:
                try:
                    location = Location.objects.get(id=location_id)
                except Location.DoesNotExist:
                    return Response({"error": "Location not found."}, status=status.HTTP_404_NOT_FOUND)
                client_data['location'] = location  # Assign the Location instance
                
            try:
                client_profile = ClientDetails.objects.create(user=user, **client_data)
                serializer = ClientDetailsSerializer(client_profile)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)            






class ClientDetailsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = ClientDetailsSerializer
    queryset = ClientDetails.objects.all()


class ClientListView (generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = ClientDetailsSerializer
    queryset = ClientDetails.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {'status': ['exact', 'in']}
    search_fields = ['first_name', 'last_name', 'status', 'date_of_birth', 'identity', 'email', 'phone_number', 'organisation',
                     'location__name', 'departement', 'gender', 'filenumber', 'city', 'Zipcode', 'infix', 'streetname', 'street_number']
    # filterset_class = ClientDetailsFilter
    ordering_fields = ['first_name', 'last_name',
                       'date_of_birth', 'city', 'streetname']
    ordering = ['-created']
    pagination_class = CustomPagination


class ClientUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientDetailsSerializer
    queryset = ClientDetails.objects.all()


class ClientDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = ClientDetailsSerializer
    queryset = ClientDetails.objects.all()

# ====================================================


class DiagnosisCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientDiagnosisSerializer


class DiagnosisRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = ClientDiagnosisSerializer
    queryset = ClientDiagnosis.objects.all()


class DiagnosisListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
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
    permission_classes = [IsAuthenticated]
    serializer_class = ClientDiagnosisSerializer
    queryset = ClientDiagnosis.objects.all()


class DiagnosisDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = ClientDiagnosisSerializer
    queryset = ClientDiagnosis.objects.all()

# =======================================================================


class ClientEmergencyContactCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientEmergencyContactSerializer


class ClientEmergencyContactRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = ClientEmergencyContactSerializer
    queryset = ClientEmergencyContact.objects.all()


class ClientEmergencyContactListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = ClientEmergencyContactSerializer
    ordering = ['-created']
    pagination_class = CustomPagination

    def get_queryset(self):
        client_id = self.kwargs['client']
        return ClientEmergencyContact.objects.filter(client=client_id)


class ClientEmergencyContactUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientEmergencyContactSerializer
    queryset = ClientEmergencyContact.objects.all()


class ClientEmergencyContactDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientEmergencyContactSerializer
    queryset = ClientEmergencyContact.objects.all()


# ==========================================================================


class ClientDocumentsUploadView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientDocumentsSerializers


class ClientDocumentsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = ClientDocumentsSerializers
    ordering = ['-created']
    pagination_class = CustomPagination

    def get_queryset(self):
        client_id = self.kwargs['client']
        return ClientDocuments.objects.filter(user=client_id)


class ClientDocumentsDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientDocumentsSerializers
    queryset = ClientDocuments.objects.all()


# ========================================================================


class ClientMedicationCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientMedicationSerializer


class ClientMedicationRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = ClientMedicationSerializer
    queryset = ClientMedication.objects.all()


class ClientMedicationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
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
    permission_classes = [IsAuthenticated]
    serializer_class = ClientMedicationSerializer
    queryset = ClientMedication.objects.all()


class ClientMedicationDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientMedicationSerializer
    queryset = ClientMedication.objects.all()


# ================================================================

class ClientAllergyCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientAllergySerializer


class ClientAllergyRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
    serializer_class = ClientAllergySerializer
    queryset = ClientAllergy.objects.all()


class ClientAllergyListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
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
    permission_classes = [IsAuthenticated]
    serializer_class = ClientAllergySerializer
    queryset = ClientAllergy.objects.all()


class ClientAllergyDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfManagement]
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


class ContractListViewGeneral(generics.ListAPIView):
    # permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = ContractSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    # filterset_class = ContractFilter
    ordering_fields = ['start_date', 'end_date',
                       'rate_per_day', 'rate_per_minute', 'rate_per_hour']
    ordering = ['-created']
    queryset = Contract.objects.all()

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
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    def post(self, request, *args, **kwargs):
        serializer = ClientTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientTypeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    queryset = ClientType.objects.all()
    serializer_class = ClientTypeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'address', 'phone_number']



class SenderRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
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
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = TemporaryFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Return the ID of the temporary file for later reference
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class GenerateInvoiceAPI(APIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]

    def post(self, request, *args, **kwargs):
        client_id = request.data.get('client_id')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')

        try:

            client = ClientDetails.objects.get(id=client_id)
            contracts = Contract.objects.filter(client=client)

            # Create an invoice instance
            invoice = Invoice(client=client, due_date=end_date)
            invoice.save()

            for contract in contracts:
                cost = contract.calculate_cost_for_period(start_date, end_date)
                
                # Create InvoiceContract instance
                InvoiceContract.objects.create(
                    invoice=invoice,
                    contract=contract,
                    pre_vat_total=cost,
                    vat_rate=invoice.vat_rate,
                    vat_amount=cost * (invoice.vat_rate / 100),
                    total_amount=cost + cost * (invoice.vat_rate / 100),
                )

            # Calculate and update invoice totals based on the created InvoiceContract instances
            invoice.update_totals()
            invoice.save()

            # Prepare the context and generate the PDF
            context = {
                'invoice_contracts': InvoiceContract.objects.filter(invoice=invoice),
                'invoice': invoice,
            }
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
            invoice.save()

            response_data = {
                'message': 'Invoice generated successfully',
                'invoice_id': invoice.id,
                'invoice_url': invoice.url,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except ClientDetails.DoesNotExist:
            return Response({'error': 'Client not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
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
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = InvoiceSerializer

    def get_queryset(self):

        client_id = self.kwargs['client_id']     
        client = get_object_or_404(Contract, id=client_id)  # Ensures the client exists
        return Invoice.objects.filter(client=client).order_by('-issue_date')


class InvoiceListViewAll(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all()
    filter_backend=[DjangoFilterBackend, SearchFilter]
    filterset_class = InvoiceFilter


class InvoiceRU(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfAuthorizedGroup]
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all()