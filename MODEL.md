# MODEL

## Overview

The platform is designed as a multi-tenant ESG emissions ingestion and analyst review system.

It supports ingestion of emissions-related activity data from multiple enterprise systems including:

* SAP exports
* Utility portal exports
* Corporate travel exports

The system normalizes incoming data into a unified emissions model and calculates CO2e emissions.

---

## Core Entities

### Client

Represents a tenant/company using the ESG platform.

Fields:

* id
* name
* industry
* created_at

---

### EmissionRecord

Stores normalized emissions activity data.

Fields:

* scope
* category
* subcategory
* activity_description
* raw_quantity
* raw_unit
* normalized_quantity
* normalized_unit
* emission_factor
* co2e_kg
* status
* suspicion_reason
* source_row_id
* period_start
* period_end

---

## Multi-Tenancy

Each emission record belongs to a specific client.

This ensures:

* tenant isolation
* separate reporting
* audit traceability

---

## Scope Classification

The system supports:

### Scope 1

Direct fuel combustion emissions.

### Scope 2

Purchased electricity emissions.

### Scope 3

Business travel and procurement emissions.

---

## Data Validation

Validation includes:

* unit normalization
* flexible date parsing
* suspicious quantity detection
* negative quantity checks

---

## Audit Workflow

Records move through:

* pending
* suspicious
* approved
* rejected

Analysts can manually review records through the dashboard.

---

## Source Tracking

Every uploaded row preserves:

* raw data
* source row ID
* source system
* ingestion timestamp

This enables auditability and traceability.
