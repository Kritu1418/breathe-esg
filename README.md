# Breathe ESG Assignment

## Project Overview

This project is an ESG (Environmental, Social, and Governance) ingestion platform developed as part of the BreatheESG internship assignment.

The system allows organizations to upload ESG-related datasets from multiple enterprise sources such as SAP exports, utility bills, and travel reports. The platform processes the uploaded data, normalizes units, calculates CO2 emissions, flags suspicious records, and enables analyst review workflows.

---

## Features

- SAP CSV ingestion
- Utility data ingestion
- Travel data ingestion
- ESG normalization engine
- CO2e emission calculation
- Suspicious data detection
- Analyst approval/rejection workflow
- Dashboard analytics
- Audit logs interface

---

## Tech Stack

### Frontend
- React
- Tailwind CSS
- Axios
- Recharts

### Backend
- Django
- Django REST Framework
- Pandas

---

## Workflow

1. Upload ESG source files
2. Backend parses and validates records
3. Units are normalized
4. CO2 emissions are calculated
5. Suspicious entries are flagged
6. Analysts can approve or reject records
7. Dashboard displays ESG analytics

---

## Deployment Links

### Frontend
https://breathe-esg-azure.vercel.app/

### Backend
https://breathe-esg-0rt4.onrender.com

---

## GitHub Repository

https://github.com/Kritu1418/breathe-esg