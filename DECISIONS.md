# DECISIONS

## Source Formats

The system supports three realistic enterprise source types:

* SAP exports
* Utility CSV exports
* Corporate travel exports

These formats were selected because they are common in enterprise ESG reporting workflows.

---

## Parsing Strategy

Separate parsers were implemented for:

* SAP data
* Utility data
* Travel data

This improves maintainability and makes future integrations easier.

---

## Unit Normalization

Different units are normalized into standard reporting units:

* kWh
* liter
* km
* kg

This ensures consistent CO2e calculations.

---

## Suspicious Record Detection

Records are automatically flagged when:

* quantity is negative
* quantity is zero
* quantity exceeds expected thresholds

This helps analysts identify data quality issues quickly.

---

## Frontend Design

A dashboard-style interface was selected to simulate enterprise ESG tooling.

The UI includes:

* analytics cards
* ingestion workflow
* approval/rejection actions
* audit status visualization

---

## Database Choice

PostgreSQL was selected because:

* it is production-grade
* widely used in enterprise systems
* supports scalable relational data storage

---

## API Design

REST APIs were used because:

* they are simple
* frontend-friendly
* commonly used in enterprise integrations
