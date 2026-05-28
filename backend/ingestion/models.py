from django.db import models
import uuid


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class IngestionBatch(models.Model):
    SOURCE_TYPES = [
        ('sap', 'SAP Fuel & Procurement'),
        ('utility', 'Utility Electricity'),
        ('travel', 'Corporate Travel'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='batches')
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    original_filename = models.CharField(max_length=255)
    uploaded_file = models.FileField(upload_to='uploads/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_rows = models.IntegerField(default=0)
    success_rows = models.IntegerField(default=0)
    failed_rows = models.IntegerField(default=0)
    suspicious_rows = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    uploaded_by = models.CharField(max_length=255, default='analyst')

    def __str__(self):
        return f"{self.client.name} - {self.source_type} - {self.uploaded_at.date()}"


class EmissionRecord(models.Model):
    SCOPE_CHOICES = [
        (1, 'Scope 1'),
        (2, 'Scope 2'),
        (3, 'Scope 3'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspicious', 'Suspicious'),
    ]

    UNIT_CHOICES = [
        ('kwh', 'kWh'),
        ('mwh', 'MWh'),
        ('liter', 'Liter'),
        ('kg', 'Kilogram'),
        ('tonne', 'Tonne'),
        ('km', 'Kilometer'),
        ('mile', 'Mile'),
        ('m3', 'Cubic Meter'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='records')
    batch = models.ForeignKey(IngestionBatch, on_delete=models.CASCADE, related_name='records')

    # scope and category
    scope = models.IntegerField(choices=SCOPE_CHOICES)
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100, blank=True)

    # activity data
    activity_description = models.TextField()
    raw_quantity = models.DecimalField(max_digits=20, decimal_places=6)
    raw_unit = models.CharField(max_length=20)
    normalized_quantity = models.DecimalField(max_digits=20, decimal_places=6)
    normalized_unit = models.CharField(max_length=20, choices=UNIT_CHOICES)

    # emission calculation
    emission_factor = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    co2e_kg = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)

    # source tracking
    source_type = models.CharField(max_length=20)
    source_row_id = models.CharField(max_length=100, blank=True)
    raw_data = models.JSONField(default=dict)

    # time period
    period_start = models.DateField()
    period_end = models.DateField()

    # review
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    suspicion_reason = models.TextField(blank=True)
    reviewed_by = models.CharField(max_length=255, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    # audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    edit_history = models.JSONField(default=list)
    is_locked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.client.name} - {self.category} - {self.period_start}"


class IngestionError(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.ForeignKey(IngestionBatch, on_delete=models.CASCADE, related_name='errors')
    row_number = models.IntegerField()
    raw_data = models.JSONField(default=dict)
    error_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Error in batch {self.batch.id} row {self.row_number}"