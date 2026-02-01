# PFEE

NEXUS – Secure Health Data Cloud PoC

Project Overview

NEXUS is a Proof of Concept (PoC) developed as part of a PFEE project.
The objective is to demonstrate the feasibility of a sovereign, secure cloud platform for managing sensitive health data, with a strong focus on consent management, access control, encryption, and auditability, in compliance with European regulations (RGPD, HDS).

This PoC does not aim to be production-ready. It demonstrates key security and governance mechanisms at a controlled and realistic prototype level.

⸻

Architecture Overview

The PoC is composed of the following components:
	•	Consent & Access API
	•	Implemented using FastAPI
	•	Manages patient consent (grant / revoke / check)
	•	Enforces access control before any data operation
	•	Secure Object Storage
	•	Implemented using MinIO (S3-compatible)
	•	Stores encrypted medical data objects
	•	Self-hosted to ensure cloud sovereignty
	•	Security Mechanisms
	•	API key–based IAM (admin / user roles)
	•	Consent-based authorization
	•	Client-side encryption (simulated)
	•	Full audit logging of all actions

⸻

Prerequisites
	•	Docker & Docker Compose
	•	Python 3.13+
	•	macOS or Linux environment

⸻

Installation & Execution

1. Start the Object Storage (MinIO)

From the project root:

docker compose up -d

MinIO Console:
	•	URL: http://localhost:9001
	•	Username: minioadmin
	•	Password: minioadmin123

⸻

2. Start the Consent API

cd consent-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

API available at:
	•	http://127.0.0.1:8000
	•	Swagger UI: http://127.0.0.1:8000/docs

⸻

API Usage Examples

Grant Consent

curl -X POST "http://127.0.0.1:8000/consent/grant?patient_id=patient123"


⸻

Upload Encrypted Medical Data (Authorized)

curl -X POST http://127.0.0.1:8000/data/upload/patient123 \
  -H "X-API-Key: admin-key"


⸻

Simulated Attack (Unauthorized Upload)

curl -X POST http://127.0.0.1:8000/data/upload/patient123 \
  -H "X-API-Key: user-key"

Expected result:
	•	HTTP 403 – access denied
	•	Action logged in audit logs

⸻

Audit Logging

All sensitive actions are logged in an audit file:

logs/audit.log

Logged events include:
	•	Consent grant / revocation
	•	Access attempts
	•	Data uploads
	•	Unauthorized actions

This ensures traceability and accountability, as required by RGPD and HDS principles.

⸻

Security & Compliance Scope

Implemented in the PoC:
	•	Explicit consent management
	•	Role-based access control
	•	Zero-Trust request validation
	•	Encrypted data storage (client-side)
	•	Sovereign hosting (self-hosted infrastructure)
	•	Full audit logging

Not implemented (out of PoC scope):
	•	Persistent databases
	•	Advanced IAM (OIDC, MFA)
	•	Hardware-backed key management (KMS / HSM)
	•	Kubernetes orchestration
	•	Performance benchmarking

These elements are addressed at architecture and design level in the project report.

⸻

Authors

Mohamed Elsonbaty & Leo LEsieur
