from django.urls import path
from .views import (
    ClientListCreateView,
    UploadDataView,
    EmissionRecordListView,
    approve_record,
    reject_record,
    IngestionErrorListView
)

urlpatterns = [

    path(
        'clients/',
        ClientListCreateView.as_view(),
        name='clients'
    ),

    path(
        'upload/',
        UploadDataView.as_view(),
        name='upload-data'
    ),

    path(
        'records/',
        EmissionRecordListView.as_view(),
        name='records'
    ),

    path(
        'records/<uuid:record_id>/approve/',
        approve_record,
        name='approve-record'
    ),

    path(
        'records/<uuid:record_id>/reject/',
        reject_record,
        name='reject-record'
    ),

    path(
        'errors/',
        IngestionErrorListView.as_view(),
        name='errors'
    ),
]