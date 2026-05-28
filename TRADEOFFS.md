# TRADEOFFS

## Real SAP Integration Not Implemented

The system currently supports SAP flat-file exports instead of direct SAP integration.

Reason:
Direct SAP integration requires enterprise credentials and SAP connector setup which is outside the scope of this assignment.

---

## Authentication Simplified

The current implementation uses a simplified analyst workflow.

Reason:
Role-based enterprise authentication was intentionally skipped to focus on ingestion, normalization, and emissions processing.

---

## PDF Parsing Not Added

The platform currently supports CSV-style structured uploads only.

Reason:
PDF extraction introduces OCR and layout complexity which was outside the project timeline.

---

## Limited Emission Factors

Only a small subset of emission factors was implemented.

Reason:
The goal was to demonstrate ingestion architecture and calculation workflow rather than full ESG coverage.

---

## Frontend Analytics Simplified

The dashboard contains lightweight charts and analytics.

Reason:
The focus was placed on backend ingestion logic and review workflow instead of advanced BI visualization.
