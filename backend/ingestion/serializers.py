from rest_framework import serializers

from .models import (
    Client,
    IngestionBatch,
    EmissionRecord,
    IngestionError
)


class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = '__all__'


class IngestionBatchSerializer(serializers.ModelSerializer):

    client_name = serializers.CharField(
        source='client.name',
        read_only=True
    )

    class Meta:
        model = IngestionBatch
        fields = '__all__'


class EmissionRecordSerializer(serializers.ModelSerializer):

    client_name = serializers.CharField(
        source='client.name',
        read_only=True
    )

    batch_source = serializers.CharField(
        source='batch.source_type',
        read_only=True
    )

    class Meta:
        model = EmissionRecord
        fields = '__all__'


class IngestionErrorSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngestionError
        fields = '__all__'