from django.contrib import admin

from .models import (
    Client,
    IngestionBatch,
    EmissionRecord,
    IngestionError
)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'slug',
        'created_at'
    )

    search_fields = (
        'name',
        'slug'
    )


@admin.register(IngestionBatch)
class IngestionBatchAdmin(admin.ModelAdmin):

    list_display = (
        'client',
        'source_type',
        'status',
        'total_rows',
        'uploaded_at'
    )

    list_filter = (
        'source_type',
        'status'
    )


@admin.register(EmissionRecord)
class EmissionRecordAdmin(admin.ModelAdmin):

    list_display = (
        'client',
        'category',
        'scope',
        'normalized_quantity',
        'normalized_unit',
        'status',
        'is_locked'
    )

    list_filter = (
        'scope',
        'status',
        'source_type'
    )

    search_fields = (
        'category',
        'activity_description'
    )


@admin.register(IngestionError)
class IngestionErrorAdmin(admin.ModelAdmin):

    list_display = (
        'batch',
        'row_number',
        'created_at'
    )