from fastapi import FastAPI, Header, HTTPException, Depends
from minio import Minio
from datetime import datetime
import logging
import os
import io

API_KEYS = {
    "admin-key": "admin",
    "user-key": "user"
}

def require_api_key(x_api_key: str = Header(...)):
    role = API_KEYS.get(x_api_key)
    if not role:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return role

app = FastAPI(title="NEXUS Consent API")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "audit.log")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    force=True
)

def audit_log(message: str):
    logging.info(message)

consents = {}

minio_client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin123",
    secure=False
)

BUCKET_NAME = "medical-data"

@app.on_event("startup")
def init_minio():
    if not minio_client.bucket_exists(BUCKET_NAME):
        minio_client.make_bucket(BUCKET_NAME)
        audit_log(f"BUCKET_CREATED name={BUCKET_NAME}")

@app.post("/consent/grant")
def grant_consent(patient_id: str):
    consents[patient_id] = {
        "granted": True,
        "timestamp": datetime.utcnow().isoformat()
    }
    audit_log(f"CONSENT_GRANTED patient_id={patient_id}")
    return {"status": "granted", "patient_id": patient_id}

@app.post("/consent/revoke")
def revoke_consent(patient_id: str):
    consents[patient_id] = {
        "granted": False,
        "timestamp": datetime.utcnow().isoformat()
    }
    audit_log(f"CONSENT_REVOKED patient_id={patient_id}")
    return {"status": "revoked", "patient_id": patient_id}

@app.get("/consent/{patient_id}")
def check_consent(patient_id: str):
    audit_log(f"CONSENT_CHECK patient_id={patient_id}")
    return consents.get(patient_id, {"granted": False})

@app.get("/data/access/{patient_id}")
def access_data(patient_id: str):
    consent = consents.get(patient_id)
    if not consent or not consent["granted"]:
        audit_log(f"ACCESS_DENIED patient_id={patient_id}")
        return {"access": "denied", "reason": "No valid consent"}
    audit_log(f"ACCESS_GRANTED patient_id={patient_id}")
    return {"access": "granted"}

@app.post("/data/upload/{patient_id}")
def upload_data(patient_id: str, role: str = Depends(require_api_key)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient privileges")

    consent = consents.get(patient_id)
    if not consent or not consent["granted"]:
        audit_log(f"UPLOAD_DENIED patient_id={patient_id}")
        return {"status": "denied", "reason": "No consent"}

    data = b"ENCRYPTED::medical_imaging_payload::AES256"
    object_name = f"{patient_id}/scan.enc"

    try:
        minio_client.put_object(
            BUCKET_NAME,
            object_name,
            data=io.BytesIO(data),
            length=len(data),
            content_type="application/octet-stream"
        )
    except Exception as e:
        audit_log(f"UPLOAD_ERROR patient_id={patient_id} error={e}")
        return {"status": "error", "detail": str(e)}

    audit_log(f"UPLOAD_OK patient_id={patient_id} object={object_name}")
    return {
        "status": "uploaded",
        "object": object_name,
        "encryption": "client-side"
    }
