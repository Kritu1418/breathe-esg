from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .models import (
    Client,
    IngestionBatch,
    EmissionRecord,
    IngestionError
)
from .serializers import (
    ClientSerializer,
    IngestionBatchSerializer,
    EmissionRecordSerializer,
    IngestionErrorSerializer
)
from .parsers import (
    SAPParser,
    UtilityParser,
    TravelParser
)


PARSER_MAP = {
    'sap': SAPParser,
    'utility': UtilityParser,
    'travel': TravelParser,
}


class ClientListCreateView(APIView):

    def get(self, request):
        clients = Client.objects.all().order_by('-created_at')
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClientSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UploadDataView(APIView):

    def post(self, request):

        client_id = request.data.get('client_id')
        source_type = request.data.get('source_type')
        uploaded_file = request.FILES.get('file')

        if not client_id:
            return Response(
                {'error': 'client_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not source_type:
            return Response(
                {'error': 'source_type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not uploaded_file:
            return Response(
                {'error': 'file is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response(
                {'error': 'client not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        batch = IngestionBatch.objects.create(
            client=client,
            source_type=source_type,
            original_filename=uploaded_file.name,
            uploaded_file=uploaded_file,
            status='processing'
        )

        parser_class = PARSER_MAP.get(source_type)

        if not parser_class:
            batch.status = 'failed'
            batch.save()

            return Response(
                {'error': 'unsupported source type'},
                status=status.HTTP_400_BAD_REQUEST
            )

        parser = parser_class()

        try:
            parsed_records, parsing_errors = parser.parse(batch.uploaded_file.path)

            success_count = 0
            suspicious_count = 0

            for record_data in parsed_records:

                emission_record = EmissionRecord.objects.create(
                    client=client,
                    batch=batch,
                    source_type=source_type,
                    scope=record_data['scope'],
                    category=record_data['category'],
                    subcategory=record_data['subcategory'],
                    activity_description=record_data['activity_description'],
                    raw_quantity=record_data['raw_quantity'],
                    raw_unit=record_data['raw_unit'],
                    normalized_quantity=record_data['normalized_quantity'],
                    normalized_unit=record_data['normalized_unit'],
                    emission_factor=record_data['emission_factor'],
                    co2e_kg=record_data['co2e_kg'],
                    source_row_id=record_data['source_row_id'],
                    raw_data=record_data['raw_data'],
                    period_start=record_data['period_start'],
                    period_end=record_data['period_end'],
                    suspicion_reason=record_data['suspicion_reason'],
                    status=record_data['status']
                )

                success_count += 1

                if emission_record.status == 'suspicious':
                    suspicious_count += 1

            for error in parsing_errors:

                IngestionError.objects.create(
                    batch=batch,
                    row_number=error['row_number'],
                    raw_data=error['raw_data'],
                    error_message=error['error_message']
                )

            batch.total_rows = success_count + len(parsing_errors)
            batch.success_rows = success_count
            batch.failed_rows = len(parsing_errors)
            batch.suspicious_rows = suspicious_count
            batch.status = 'completed'
            batch.processed_at = timezone.now()
            batch.save()

            return Response({
                'message': 'file processed successfully',
                'batch_id': str(batch.id),
                'total_rows': batch.total_rows,
                'success_rows': batch.success_rows,
                'failed_rows': batch.failed_rows,
                'suspicious_rows': batch.suspicious_rows,
            })

        except Exception as e:

            batch.status = 'failed'
            batch.save()

            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EmissionRecordListView(APIView):

    def get(self, request):

        records = EmissionRecord.objects.all().order_by('-created_at')

        source_type = request.GET.get('source_type')
        status_filter = request.GET.get('status')
        scope = request.GET.get('scope')

        if source_type:
            records = records.filter(source_type=source_type)

        if status_filter:
            records = records.filter(status=status_filter)

        if scope:
            records = records.filter(scope=scope)

        serializer = EmissionRecordSerializer(records, many=True)

        return Response(serializer.data)


@api_view(['POST'])
def approve_record(request, record_id):

    try:
        record = EmissionRecord.objects.get(id=record_id)
    except EmissionRecord.DoesNotExist:
        return Response(
            {'error': 'record not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    if record.is_locked:
        return Response(
            {'error': 'record already locked'},
            status=status.HTTP_400_BAD_REQUEST
        )

    record.status = 'approved'
    record.reviewed_by = request.data.get('reviewed_by', 'analyst')
    record.reviewed_at = timezone.now()
    record.review_notes = request.data.get('review_notes', '')
    record.is_locked = True

    record.save()

    return Response({
        'message': 'record approved successfully'
    })


@api_view(['POST'])
def reject_record(request, record_id):

    try:
        record = EmissionRecord.objects.get(id=record_id)
    except EmissionRecord.DoesNotExist:
        return Response(
            {'error': 'record not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    if record.is_locked:
        return Response(
            {'error': 'record already locked'},
            status=status.HTTP_400_BAD_REQUEST
        )

    record.status = 'rejected'
    record.reviewed_by = request.data.get('reviewed_by', 'analyst')
    record.reviewed_at = timezone.now()
    record.review_notes = request.data.get('review_notes', '')

    record.save()

    return Response({
        'message': 'record rejected successfully'
    })


class IngestionErrorListView(APIView):

    def get(self, request):

        errors = IngestionError.objects.all().order_by('-created_at')

        serializer = IngestionErrorSerializer(errors, many=True)

        return Response(serializer.data)